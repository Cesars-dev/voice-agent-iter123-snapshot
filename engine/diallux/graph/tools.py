"""Tool executor — V2 production hardening of the verbatim executor.

Everything from V1 (repeat guard, extract writes, HMAC webhooks, leak-math
port, transitions, end_call) PLUS:

  1. SERVER_OWNED_DVS protection — extract tools can no longer write the
     server-owned booleans/values (slot_verified, data_verified, phone_confirmed,
     booking_verified, today_date, ...). The LLM cannot fabricate progress.
  2. Hard gates on transitions — `transition_to_X` only swaps state when every
     `required` param of the edge schema is truthy in dvs. Otherwise the tool
     answers {"status": "gate_failed", "missing": [...]} and the state holds.
     Retell's intent, finally enforced deterministically.
  3. Webhook retries — connection-level retries with backoff (httpx transport)
     so a VPS hiccup doesn't fail a booking turn.
  4. Typed dvs — patches flow through schema.DynamicVariables for validation
     and coercion ("" not null; ints coerced).
"""
from __future__ import annotations

import hashlib
import hmac
import json
import math
import re
import time
from typing import Any

import httpx

from ..schema import SERVER_OWNED_DVS, DynamicVariables


class ToolOutcome(dict):
    """Result of one tool call: what the model sees + state side effects."""

    @property
    def response(self) -> dict:
        return dict(self.get("response") or {})

    @property
    def dvs_patch(self) -> dict:
        return dict(self.get("dvs_patch") or {})

    @property
    def new_state(self) -> str | None:
        return self.get("new_state")

    @property
    def ended(self) -> bool:
        return bool(self.get("ended"))


# iter14: LLM-facing gate-failure strings — name the property, state its current
# value, give the exact remedy step. One per param that can fail a gate.
# iter30: a spoken goodbye is remembered per call — a silent end_call that
# follows an already-spoken goodbye is LEGITIMATE (the model speaks the goodbye
# in one round, hangs up in the next). Only a hangup with NO goodbye ever
# spoken stays blocked (iter16 rule, now engine-remembered instead of
# same-response-only).
_GOODBYE_RE = re.compile(
    r"\b(goodbye|bye|bye-bye|take care|have a great|talk soon|cheers)\b", re.IGNORECASE)

_WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


GATE_FAIL_MESSAGES: dict[str, str] = {    "is_calling_best_number": (
        "is_calling_best_number is unanswered — ask if the number they're calling from is their "
        "best contact number, then call record_reach_details with true or false."
    ),
    "phone_confirmed": (
        "phone_confirmed is false — read the number back, get a clear yes, then call "
        "set_callback_number with the digits."
    ),
    "contact_details_completed": (
        "contact_details_completed is false — first name, last name, company, timezone and best "
        "number aren't all done; finish what's open, then set it."
    ),
    "first_name": "first_name is empty — ask for it, then call extract_person_details.",
    "last_name": "last_name is empty — ask for it, then call extract_person_details.",
    "company_name": "company_name is empty — ask for it, then call extract_person_details.",
    "prospect_timezone": (
        "prospect_timezone is empty — get their city or local time, then call extract_contact_timezone."
    ),
    "callback_number": (
        "callback_number is empty — confirm their best number, then call set_callback_number."
    ),
    "slot_verified": (
        "slot_verified is false — fix each problem in validate_lead's actions list, then re-call "
        "validate_lead."
    ),
    "data_verified": (
        "data_verified is false — speak each action from verify_lead_data, correct the details, "
        "re-call until ok."
    ),
    "booking_verified": (
        "booking_verified is false — no accepted booking yet; retry create_livecall_booking, then "
        "record_booking_uid."
    ),
}


class ToolExecutor:
    def __init__(
        self,
        settings,
        llm_json: dict,
        tracer=None,
        http_client: httpx.AsyncClient | None = None,
        slots_warm: dict | None = None,      # iter40 L2: shared warm store (CallRuntime-owned)
    ):
        self.settings = settings
        self.llm_json = llm_json
        self.states = {s["name"]: s for s in llm_json.get("states", [])}
        self.general_tools = llm_json.get("general_tools", [])
        self.tracer = tracer
        self.slots_warm = slots_warm if slots_warm is not None else {}
        if http_client is not None:
            self.http = http_client
            self._owns_http = False
        else:
            transport = httpx.AsyncHTTPTransport(retries=2)   # V2: connection retries
            self.http = httpx.AsyncClient(timeout=settings.webhook_timeout_s, transport=transport)
            self._owns_http = True
        self._last_call: tuple[str, str] | None = None
        self._last_slots_date: str | None = None   # iter40 T6: last SUCCESSFUL slots date
        # iter123 R5: per-turn executed-set — (name, args) -> the ToolOutcome
        # of a call that EXECUTED OK this turn. Identical re-sends short-
        # circuit with the cached reply (no HTTP, no freeze); failures NEVER
        # enter the set (honest retries always run). Cleared by
        # reset_repeat_guard (turn start + cancelled generations).
        self._executed_ok: dict[tuple[str, str], ToolOutcome] = {}
        self.trace: list[dict] = []
        self.gate_rejections: list[dict] = []      # observability: every refused transition
        self.end_call_blocks: list[dict] = []      # observability: refused booking-claim hangups

    async def aclose(self):
        if self._owns_http:
            await self.http.aclose()

    # ------------------------------------------------------------------ #
    async def execute(self, name: str, args: dict, dvs: dict, state_name: str = "",
                      spoken_text: str = "", last_spoken: str = "") -> ToolOutcome:
        t0 = time.perf_counter()
        obs = self.tracer.start_tool(name, args, state_name) if self.tracer else None
        # iter123 R5: the diary ledger — key on the SAME fingerprint the
        # repeat guard uses (pre-prefill args, byte-compat with _last_call).
        _key = (name, json.dumps(args or {}, sort_keys=True))
        try:
            outcome = await self._execute_inner(name, args, dvs, state_name, spoken_text,
                                                last_spoken)
        except Exception as exc:
            outcome = ToolOutcome(response={
                "ok": False, "error": "tool_exception", "message": f"{type(exc).__name__}: {exc}"[:200]
            })
        # iter123 R5: record successes in the per-turn diary; roll the
        # consecutive-guard cell BACK on failure — it was set at dispatch, so
        # without the rollback a FAILED call (500, gate_failed, reject) would
        # bounce its own identical retry with `already_captured` (the F5b
        # grudge bug). end_call stays exempt (re-callable by design).
        if name != "end_call":
            if _outcome_failed(outcome.response):
                if self._last_call == _key:
                    self._last_call = None
            else:
                self._executed_ok[_key] = outcome
        # iter40 T6: tag prefilled-date responses; remember the last SUCCESSFUL
        # dated slots call for the next prefill.
        if name == "query_livecall_slots":
            prefilled = bool((args or {}).pop("_prefilled", None))
            resp = outcome.response
            if prefilled and isinstance(resp, dict):
                resp = dict(resp)
                resp["source"] = "prefill"
                outcome["response"] = resp
            if ((args or {}).get("slot_target_date")
                    and isinstance(resp, dict) and resp.get("ok") and resp.get("slots")):
                self._last_slots_date = args["slot_target_date"]
        # iter62 (FIND-29 family): record_reach_details(true) with NO
        # callback_number is a guaranteed dead end on mic transport (no
        # caller-ID to seed) — the webhook answers ok/"seeded stands" and
        # the ConfirmSlots gate then blocks with no scripted recovery.
        # Hand the model the next step HERE; the webhook's dvs_patch
        # (phone_confirmed) stands. Non-empty callback_number or a NO
        # answer = byte-identical to today.
        if name == "record_reach_details" \
                and (args or {}).get("is_calling_best_number") is True \
                and not str((dvs or {}).get("callback_number") or "").strip():
            resp = dict(outcome.response or {})
            resp["status"] = "need_digits"
            resp["instruction"] = ("Ask: What's the best number to reach you? "
                                   "Then call set_callback_number with the "
                                   "exact digits they spoke.")
            outcome["response"] = resp
        if self.tracer:
            self.tracer.finish_tool(obs, outcome.response, time.perf_counter() - t0)
        self.trace.append({"tool": name, "args": args, "resp": outcome.response,
                           "dvs_patch": outcome.dvs_patch,
                           "new_state": outcome.new_state, "ended": outcome.ended})
        return outcome

    def reset_repeat_guard(self) -> None:
        """iter112: clear the same-call repeat guard.

        A CANCELLED generation (eager/speculative turn discarded on caller
        resume, barge-in rerun) may have executed tools whose dvs patches
        never landed (the graph write was dropped with the generation). The
        retry turn re-proposes the same call; without this reset the guard
        answers `already_captured` for values that were never stored — E3
        (2026-10-13 06:26): empty `requested_slot` → empty `slot_options` →
        `verify_lead_data` `unfixable_format` → no booking. Only `_last_call`
        is cleared; `_last_slots_date` is factual calendar memory and keeps
        its t55 prefill value.

        iter123 R5: the per-turn executed-set diary clears here too (same
        cancelled-generation hazard — patches never landed, cached replies
        would be stale truth)."""
        self._last_call = None
        self._executed_ok.clear()

    async def _execute_inner(self, name: str, args: dict, dvs: dict, state_name: str = "",
                             spoken_text: str = "", last_spoken: str = "") -> ToolOutcome:
        # 1. Repeat-call guard (verbatim from engine.py)
        # iter16: end_call is exempt — a blocked end_call (silent-hangup gate) must be
        # re-callable with identical args in the next round.
        # iter123 R5: the per-turn executed-set diary is checked FIRST for the
        # non-consecutive repeat (A,B,A): an identical (name, args) that
        # already EXECUTED OK this turn returns its cached reply with the
        # side effects stripped (patches/state already landed once — G5).
        # The consecutive case keeps today's `already_captured` answer below.
        key = (name, json.dumps(args, sort_keys=True))
        if name != "end_call":
            # Order is load-bearing: the CONSECUTIVE case keeps today's
            # byte-identical contract (`already_captured`, plus the iter112
            # requested_slot honesty release) BEFORE the diary — a repeat of
            # the immediately-prior call must answer exactly as today. The
            # diary then catches the NON-consecutive repeat (A,B,A).
            if self._last_call == key:
                if (name == "query_livecall_slots"
                        and not (dvs or {}).get("requested_slot")):
                    # iter112 belt-and-braces: the guard is only honest when
                    # the values REALLY landed — a missing requested_slot
                    # proves the prior capture's patch never committed (e.g.
                    # a cancelled generation that set the guard from a lost
                    # write). Release and re-execute live.
                    self._last_call = None
                else:
                    return ToolOutcome(response={
                        "status": "already_captured",
                        "message": ("Values are already stored as dynamic variables. Do NOT call this "
                                    "tool again — proceed to the next step in the flow."),
                    })
            else:
                _cached = self._executed_ok.get(key)
                # iter112 honesty rule extends to the diary: never serve a
                # cached slots reply while requested_slot never landed.
                if _cached is not None and not (
                        name == "query_livecall_slots"
                        and not (dvs or {}).get("requested_slot")):
                    return ToolOutcome(response=dict(_cached.response))
            self._last_call = key

        # 2-4. state tools + general tools
        # iter40 L2: the model's first slots call (dated, empty uids, freeze
        # mode — t40 shape) is answered from the bg-warmed payload when fresh —
        # kills the 2.5s synchronous webhook spike. Everything else (uid
        # re-freeze, preferred_time, stale, mismatched date) → live webhook.
        # iter123 R3: the executor handshake — args checked against the
        # schema/rules BEFORE anything executes. Ordering is load-bearing:
        # `_prefill_slots_date` runs FIRST (an omitted date is auto-fixed,
        # never rejected), the pre-flight SECOND, warm-serve / live webhook
        # after. A violation returns {status:"rejected", silent:true, fix}
        # with NO execute, NO freeze, nothing spoken — the model re-sends
        # with the fix next round (the Dave null-date class can no longer
        # reach — or freeze — the live endpoint).
        if name == "query_livecall_slots":
            args = self._prefill_slots_date(args, dvs)
            rejected = self._preflight_args(name, args, dvs)
            if rejected is not None:
                return rejected
            warm_outcome = self._slots_prefetch_outcome(args)
            if warm_outcome is not None:
                return warm_outcome
        else:
            rejected = self._preflight_args(name, args, dvs)
            if rejected is not None:
                return rejected
        for t in list(self.states.get(state_name, {}).get("tools", [])) + list(self.general_tools):
            if t.get("name") != name:
                continue
            if t.get("type") == "extract_dynamic_variable":
                return self._exec_extract(t, args)
            if t.get("type") == "custom":
                return await self._exec_custom(t, args)
            if t.get("type") == "code":
                return self._exec_code(t, dvs)

        # 5. transitions — HARD GATED (V2)
        if name.startswith("transition_to_"):
            dest = name[len("transition_to_"):]
            if dest not in self.states:
                return ToolOutcome(response={"status": "unknown_state", "state": dest})
            edge = next((e for e in self.states.get(state_name, {}).get("edges", [])
                         if e.get("destination_state_name") == dest), None)
            if edge is None:
                # the state machine itself is enforced: only edges that exist
                # in the deployed artifact can be taken
                return ToolOutcome(response={
                    "status": "invalid_transition",
                    "message": (f"There is no transition from {state_name} to {dest}. "
                                "Follow the conversation flow."),
                })
            ok, missing = self._gate_check_edge(edge, dvs)
            if not ok:
                self.gate_rejections.append(
                    {"tool": name, "state": state_name, "dest": dest, "missing": missing})
                return ToolOutcome(response={
                    "status": "gate_failed",
                    "missing": missing,
                    "message": ("Transition NOT taken: " + " ".join(
                        GATE_FAIL_MESSAGES.get(
                            p, f"{p} is not set yet — complete that step in the state prompt first.")
                        for p in missing)),
                })
            return ToolOutcome(response={"status": "ok", "state": dest}, new_state=dest)

        # 6. end_call — booking-claim truth gate (iter8, Surgeon v5-pgvector-gpt52-argfix).
        # Live-observed: gpt-4.1 said "I've got you down for 3:30" + end_call with ZERO
        # booking tools fired (Danny/Marcus). The model must never be able to hang up
        # claiming a booking it didn't make — deterministic, not prompt-trust.
        # iter16: silent-hangup gate — end_call with empty reply text is rejected
        # UNLESS a goodbye was already spoken earlier in the call (iter30: the
        # goodbye round and the hangup round are legitimately separate LLM trips;
        # demanding same-response co-emit caused 12-round silent hammer loops).
        if name == "end_call":
            if dvs.get("livecall_agreed") and not (dvs.get("slot_verified") or dvs.get("booking_confirmed")):
                self.end_call_blocks.append({"state": state_name})
                return ToolOutcome(response={
                    "status": "end_call_blocked",
                    "message": ("The caller agreed to a live call but no booking has been "
                                "completed. You may NOT end the call as if it were booked. "
                                "Either complete the booking flow now (ConfirmSlots → verify "
                                "→ booking) or honestly tell the caller the booking did not "
                                "happen."),
                })
            # iter40 T6b: skip-the-machine gate, scoped to CLOSER ONLY (live
            # Maria 2026-09-09: whole funnel role-played as speech in Closer,
            # zero flow tools, polite hangup). closer_completed is Closer's own
            # completion flag — and every LATER state requires it to exist
            # (edge gates), so only pre-completion Closer is gated. One
            # refusal with a repair message; second attempt accepted (iter31
            # dampener escape — legit mid-pitch declines still end). Silent
            # end_calls stay with the iter16/31 gate; goodbye memory (iter30)
            # preserved; iter8 untouched. Intake/Discovery hostile exits and
            # Closing are NOT gated (all three contracts re-verified by suite).
            closer_refusals = sum(
                1 for b in self.end_call_blocks if b.get("reason") == "closer_skip_endcall")
            if (state_name == "Closer"
                    and not dvs.get("closer_completed")
                    and closer_refusals == 0
                    and (spoken_text or "").strip()
                    and not (last_spoken and _GOODBYE_RE.search(last_spoken))):
                self.end_call_blocks.append(
                    {"state": state_name, "reason": "closer_skip_endcall"})
                return ToolOutcome(response={
                    "status": "end_call_blocked",
                    "message": ("You are ending the call from the pitch stage without having "
                                "completed it (closer_completed is not set). You skipped the "
                                "flow: fire the extract tools for what the caller told you "
                                "(leak inputs, details), complete the pitch step, then "
                                "continue the conversation — do not hang up here."),
                })
            if not (spoken_text or "").strip():
                if last_spoken and _GOODBYE_RE.search(last_spoken):
                    return ToolOutcome(response={
                        "status": "call_ended", "goodbye_already_spoken": True}, ended=True)
                self.end_call_blocks.append({"state": state_name, "reason": "empty_text"})
                return ToolOutcome(response={
                    "status": "end_call_blocked",
                    "message": ("You called end_call with no spoken text. FIRST write the "
                                "warm goodbye sentence (per ##call-closing-kb##) as your reply "
                                "text in this same response, THEN call end_call again."),
                })
            return ToolOutcome(response={"status": "call_ended"}, ended=True)

        if name == "memory_note":
            # iter48b: LITE_NOOP_TOOL — a pacing dummy the model must never
            # call; if it does anyway, swallow it (no dvs writes, no routing).
            return ToolOutcome(response={"status": "noted"})

        return ToolOutcome(response={"status": "unknown_tool", "name": name})

    # ------------------------------------------------------------------ #
    def _slots_prefetch_outcome(self, args: dict) -> ToolOutcome | None:
        """iter40 L2: serve the model's slots call from the warm store.

        Exact arg-match required (warm = the model's own first-call shape,
        freeze-mode, per frozen OTEL t40 evidence): same `slot_target_date`,
        empty/absent `current_reservation_uids`, no `preferred_time` value.
        Warm payload must be ok with non-empty slots and < ttl old. Response
        gains `source: "prefetch"`; dvs patch mirrors response_variables.
        Any other call (dated mismatch, non-empty uids, named time, stale,
        error payload) → None → live webhook.
        """
        if not getattr(self.settings, "slots_prefetch", False):
            return None
        a = args or {}
        if a.get("current_reservation_uids") or a.get("preferred_time"):
            return None
        date = str(a.get("slot_target_date") or "").strip()
        if not date:
            return None
        warm = (self.slots_warm or {}).get(date)
        if not warm:
            return None
        body = warm.get("payload") or {}
        if not (isinstance(body, dict) and body.get("ok") and body.get("slots")):
            return None
        ttl = float(getattr(self.settings, "slots_prefetch_ttl_s", 120.0))
        if time.monotonic() - warm.get("ts", 0.0) > ttl:
            return None
        if warm.get("tz") and a.get("timezone") and warm["tz"] != a["timezone"]:
            return None
        resp = dict(body)
        resp["source"] = "prefetch"
        tool = self._tool_def("query_livecall_slots")
        return ToolOutcome(response=resp, dvs_patch=self._patch_from_body(tool, resp))

    # ------------------------------------------------------------------ #
    def _preflight_args(self, name: str, args: dict, dvs: dict) -> ToolOutcome | None:
        """iter123 R3: the executor arg handshake — checked BEFORE execute.

        Rules are engine policy (module-level _ARG_RULES), not Retell-artifact
        config: the OpenAI-side `required` schema stays the first line of
        defense at generation time; this is the semantic second line (shape
        the schemas cannot express: null dates, stale uids, empty picks).
        A violation returns {status:"rejected", silent:true, fix} — NO
        execute, NO freeze, nothing spoken; the model re-sends with the fix
        next round. Rejected calls are never recorded in the executed-set
        diary (execute() rolls them back), so a fixed retry always runs.

        GO booleans (documented per plan): `slot_verified` (validate_lead)
        gates transition_to_VerifyLead; `data_verified` (verify-lead-data)
        gates transition_to_Booking. Both are SERVER-OWNED — the model never
        sets them."""
        rules = _ARG_RULES.get(name)
        if not rules:
            return None
        a = args or {}
        for arg, required, ok, fix in rules:
            if arg not in a:
                if required:
                    return ToolOutcome(response={
                        "status": "rejected", "silent": True, "fix": fix})
                continue
            if not ok(a.get(arg), dvs):
                return ToolOutcome(response={
                    "status": "rejected", "silent": True, "fix": fix})
        return None

    def _tool_def(self, name: str) -> dict:
        for t in self.general_tools:
            if t.get("name") == name:
                return t
        for s in self.states.values():
            for t in s.get("tools", []):
                if isinstance(t, dict) and t.get("name") == name:
                    return t
        return {}

    def _patch_from_body(self, t: dict, body: dict) -> dict:
        """response_variables → dvs patch (shared by live webhook + prefetch)."""
        return {
            dv_name: body[resp_key]
            for dv_name, resp_key in (t.get("response_variables") or {}).items()
            if isinstance(body, dict) and resp_key in body and body[resp_key] not in (None, "")
        }

    # ------------------------------------------------------------------ #
    def _prefill_slots_date(self, args: dict, dvs: dict) -> dict:
        """iter40 T6: auto-fill `slot_target_date` when the model omits it.

        The t55 failure mode: after an error round the model dropped the date →
        endpoint `no_start_time` → dead-air re-ask of a day the caller already
        gave. Fill from the last SUCCESSFUL slots date on this call; else from
        a day word in {{requested_slot}} (today/tomorrow/weekday via
        {{today_date}}). Nothing known → unchanged (live no_start_time).
        Mutates `args` IN PLACE (execute() reads the `_prefilled` flag after).
        """
        if args is None:
            args = {}
        if args.get("slot_target_date"):
            return args
        date = self._last_slots_date or self._date_from_requested_slot(dvs)
        if date:
            args["slot_target_date"] = date
            args["_prefilled"] = True
        return args

    def _date_from_requested_slot(self, dvs: dict):
        """Day word in {{requested_slot}} → concrete date via {{today_date}}."""
        import datetime as _dt
        try:
            from zoneinfo import ZoneInfo as _Z
            text = str(dvs.get("requested_slot") or "").strip().lower()
            m = re.match(r"^(today|tomorrow|monday|tuesday|wednesday|thursday|"
                         r"friday|saturday|sunday)\b", text)
            if not m:
                return None
            today_raw = str(dvs.get("today_date") or "").strip()
            if today_raw:
                today = _dt.datetime.strptime(today_raw[:10], "%Y-%m-%d").date()
            else:
                tz = str(dvs.get("prospect_timezone") or "America/New_York")
                today = _dt.datetime.now(_Z(tz)).date()
            word = m.group(1)
            if word == "today":
                return today.isoformat()
            if word == "tomorrow":
                return (today + _dt.timedelta(days=1)).isoformat()
            return (today + _dt.timedelta(
                days=(_WEEKDAYS.index(word) - today.weekday()) % 7 or 7)).isoformat()
        except Exception:
            return None

    # ------------------------------------------------------------------ #
    def _exec_extract(self, t: dict, args: dict) -> ToolOutcome:
        wrote: dict = {}
        rejected: list[str] = []
        for v in t.get("variables", []):
            val = args.get(v["name"])
            if val in (None, ""):
                continue
            if v["name"] in SERVER_OWNED_DVS:           # V2 hard gate: server-owned
                rejected.append(v["name"])
                continue
            wrote[v["name"]] = val
        # validate through the typed model (coercion + type safety)
        merged = DynamicVariables.from_flat({**{"__x": 1}, **wrote})
        clean = {k: merged.to_flat()[k] for k in wrote}
        resp = {"status": "ok", "written": clean}
        if rejected:
            resp["rejected_server_owned"] = rejected
            resp["note"] = ("These values are set by the system automatically and cannot be "
                            "captured manually: " + ", ".join(rejected))
        return ToolOutcome(response=resp, dvs_patch=clean)

    # ------------------------------------------------------------------ #
    def _gate_check_edge(self, edge: dict, dvs: dict) -> tuple[bool, list[str]]:
        """`required` params must be truthy in dvs; `presence_required` params
        must be non-null (answered — false is a legitimate value, e.g. the
        caller said the calling number is NOT their best number)."""
        params = (edge or {}).get("parameters", {})
        required = params.get("required", [])
        presence = params.get("presence_required", [])
        missing = [p for p in required if not dvs.get(p)]
        unanswered = [p for p in presence if dvs.get(p) is None or dvs.get(p) == ""]
        return (not missing and not unanswered, missing + unanswered)

    # ------------------------------------------------------------------ #
    async def _exec_custom(self, t: dict, args: dict) -> ToolOutcome:
        """HMAC-signed webhook (verbatim contract) + retries."""
        from urllib.parse import urlencode

        url = t["url"]
        method = t.get("method", "POST").upper()
        payload = args if t.get("args_at_root") else {"args": args}
        raw = json.dumps(payload).encode()
        sign_target = raw if method != "GET" else b""
        headers = {
            "Content-Type": "application/json",
            "X-Retell-Signature": self._sign(sign_target, url),
        }
        if method == "GET":
            query = dict(t.get("query_params") or {})
            query.update(payload)
            url = url + ("&" if "?" in url else "?") + urlencode(query)
        elif t.get("query_params"):
            url = url + "?" + urlencode(t.get("query_params"))
        timeout = (t.get("timeout_ms") or 15000) / 1000.0

        body: dict = {}
        for attempt in range(2):                     # V2: one retry on 5xx/transport error
            try:
                if method == "GET":
                    resp = await self.http.get(url, headers=headers, timeout=timeout)
                else:
                    resp = await self.http.post(url, content=raw, headers=headers, timeout=timeout)
                try:
                    body = resp.json()
                except ValueError:
                    body = {}
                if resp.status_code >= 500 and attempt == 0:
                    await _sleep_backoff(attempt)
                    continue
                if resp.status_code >= 400:
                    body = dict(body) or {}
                    body.setdefault("ok", False)
                    body.setdefault("error", f"http_{resp.status_code}")
                break
            except httpx.RequestError as exc:
                body = {"ok": False, "error": "request_failed", "message": str(exc)[:200]}
                if attempt == 0:
                    await _sleep_backoff(attempt)
                    continue

        patch: dict = self._patch_from_body(t, body)
        return ToolOutcome(response=body, dvs_patch=patch)

    def _sign(self, raw: bytes, url: str = "") -> str:
        key = self.settings.retell_api_key
        if self.settings.slots_webhook_key and ("check_availability" in url or "book-livecall" in url):
            key = self.settings.slots_webhook_key
        ts = str(int(time.time() * 1000))
        digest = hmac.new(key.encode(), raw + ts.encode(), hashlib.sha256).hexdigest()
        return f"v={ts},d={digest}"

    # ------------------------------------------------------------------ #
    def _exec_code(self, t: dict, dvs: dict) -> ToolOutcome:
        if t["name"] != "calculate_monthly_leak":
            return ToolOutcome(response={"ok": False, "error": "unsupported_code_tool", "name": t["name"]})
        result, patch = calculate_monthly_leak(dvs)
        return ToolOutcome(response=result, dvs_patch=patch)


async def _sleep_backoff(attempt: int):
    await __import__("asyncio").sleep(0.3 * (attempt + 1))


# --------------------------------------------------------------------------- #
# iter123 R3: the executor arg-handshake rules — engine policy, checked by
# ToolExecutor._preflight_args BEFORE execute. Rule tuple:
#   (arg_name, required, ok(value, dvs) -> bool, fix_message)
# required=True → the arg must be present AND pass; required=False → checked
# only when the model sent it. A violation → {status:"rejected", silent:true,
# fix} — no execute, no freeze, nothing spoken (the Dave null-date class can
# no longer reach the live freeze endpoint). GO booleans for the flow:
# `slot_verified` (validate_lead) → transition_to_VerifyLead;
# `data_verified` (verify-lead-data) → transition_to_Booking.
def _rule_date(v, dvs) -> bool:
    return not str(v or "").strip() or bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(v).strip()))


def _rule_uids_match(v, dvs) -> bool:
    got = str(v or "").strip()
    want = str((dvs or {}).get("slot_reservation_uids") or "").strip()
    if not want:
        return True
    return got == want


def _rule_nonempty(v, dvs) -> bool:
    return bool(str(v or "").strip())


_ARG_RULES: dict[str, list[tuple[str, bool, Any, str]]] = {
    "query_livecall_slots": [
        ("slot_target_date", False, _rule_date,
         "slot_target_date must be a YYYY-MM-DD date or omitted for as-soon-as-possible "
         "— re-send the day in YYYY-MM-DD form (never null/empty text)"),
        ("current_reservation_uids", False, _rule_uids_match,
         "current_reservation_uids must be empty or exactly the live {{slot_reservation_uids}} "
         "value — re-send the stored value verbatim"),
    ],
    "validate_lead": [
        ("selected_time", True, _rule_nonempty,
         "selected_time is missing — re-send the caller's pick exactly as captured; "
         "if no pick was captured yet, ask the caller which slot they want first"),
    ],
    "verify_lead_data": [
        ("selected_time", True, _rule_nonempty,
         "selected_time is missing — re-send the caller's pick exactly as captured; "
         "if no pick was captured yet, ask the caller which slot they want first"),
    ],
    "create_livecall_booking": [
        ("time", True, _rule_nonempty,
         "time is missing — re-send {{selected_time}} exactly as captured"),
        ("slot_reservation_uids", True, _rule_uids_match,
         "slot_reservation_uids must be the live {{slot_reservation_uids}} value verbatim "
         "— never modify, never invent"),
    ],
}


def _outcome_failed(resp: dict) -> bool:
    """iter123 R5: the failure set for the executed-set diary / guard rollback.
    Anything here NEVER enters the diary and rolls the consecutive-guard cell
    back, so an honest identical retry re-executes live."""
    if not isinstance(resp, dict):
        return True
    if resp.get("ok") is False:
        return True
    return resp.get("status") in {
        "error", "tool_exception", "request_failed", "unknown_tool", "unknown_state",
        "invalid_transition", "gate_failed", "end_call_blocked", "rejected",
        "book_failed",
    }


# --------------------------------------------------------------------------- #
def _first_num(s: Any) -> float:
    """JS parity: String(s||'').replace(/,/g,'').match(/\\d+(\\.\\d+)?/) -> Number(m[0]) or NaN."""
    text = str(s if s not in (None, "") else "").replace(",", "")
    m = re.search(r"(\d+(\.\d+)?)", text)
    return float(m.group(1)) if m else float("nan")


# --------------------------------------------------------------------------- #
# iter114 T2: word-number resolution for the leak-math inputs. _first_num
# stays byte-parity with the deployed JS (parity-tested); this is an ADDITIVE
# resolver used only by resolve_calls.
_WORD_NUMS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
    "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60,
    "seventy": 70, "eighty": 80, "ninety": 90, "dozen": 12,
    "couple": 2, "few": 3,
}
_WORD_NUM_RE = re.compile(
    r"\b(?:(twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)"
    r"[ -]?(one|two|three|four|five|six|seven|eight|nine)?"
    r"|(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
    r"thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen)"
    r"|(dozen|couple|few))\b", re.IGNORECASE)


def _word_num(s: Any) -> float:
    """'about fifteen a week' -> 15. NaN when no word number is present."""
    text = str(s if s not in (None, "") else "").lower()
    if not text:
        return float("nan")
    m = _WORD_NUM_RE.search(text)
    if not m:
        return float("nan")
    if m.group(1):                                  # tens [ -]units
        tens = _WORD_NUMS[m.group(1)]
        units = _WORD_NUMS.get(m.group(2) or "", 0)
        return float(tens + units)
    if m.group(3):
        return float(_WORD_NUMS[m.group(3)])
    return float(_WORD_NUMS[m.group(4)])


def resolve_calls(dvs: dict, normalize: bool = True) -> tuple[float, str]:
    """iter114 T2: resolve the missed-calls input for the leak math.
    Precedence: numeric missed_calls_weekly > call_volume (only when its
    phrasing says "week" — digits or word numbers) > missed_calls_daily × 5.
    Returns (value, source); ("nan", "") when nothing resolves.
    normalize=False = the legacy weekly/daily-only resolution (T2 rollback).

    Why call_volume outranks daily×5: extraction sometimes writes the
    caller's words to call_volume while also writing a mis-derived daily
    figure (E4c: daily=2 from the caller's "15/week" — daily×5=10
    under-computes the true 15). The "…a week" string IS the caller's
    answer. Daily-phrased call_volume ("10-15 a day") is deliberately NOT
    parsed as weekly — it falls through to missed_calls_daily × 5."""
    w = _first_num(dvs.get("missed_calls_weekly"))
    if math.isfinite(w) and w > 0:
        return w, "weekly"
    if normalize:
        cv = str(dvs.get("call_volume") or "")
        if cv and "week" in cv.lower():
            n = _first_num(cv)
            if not (math.isfinite(n) and n > 0):
                n = _word_num(cv)
            if math.isfinite(n) and n > 0:
                return n, "call_volume"
    d = _first_num(dvs.get("missed_calls_daily"))
    if math.isfinite(d) and d > 0:
        return d * 5.0, "daily"
    return float("nan"), ""


def leak_inputs_present(dvs: dict, normalize: bool = True) -> bool:
    # iter65 T3: daily-aware — a DAILY missed-calls count satisfies the
    # calls input (calculate_monthly_leak resolves daily × 5).
    # iter114 T2: resolution unified in resolve_calls (weekly > call_volume
    # "…week" phrasing > daily × 5).
    w, _ = resolve_calls(dvs, normalize=normalize)
    calls_ok = math.isfinite(w) and w > 0
    r = _first_num(dvs.get("close_rate_pct"))
    a = _first_num(dvs.get("avg_job_value"))
    return calls_ok and all(math.isfinite(x) and x > 0 for x in (r, a))


def calculate_monthly_leak(dvs: dict, normalize: bool = True) -> tuple[dict, dict]:
    """The deployed Retell code tool, ported (legacy cases parity-tested).
    iter65 T3: explicit weekly WINS; a DAILY count fills the gap (×5 — 5
    business days). iter114 T2: a call_volume string with "…week" phrasing
    resolves when no numeric weekly exists (digits or word numbers:
    "about fifteen a week" -> 15). Resolved values patch missed_calls_weekly
    (model-writable, NOT server-owned). normalize=False = legacy path."""
    w, source = resolve_calls(dvs, normalize=normalize)
    r = _first_num(dvs.get("close_rate_pct"))
    a = _first_num(dvs.get("avg_job_value"))
    missing = []
    if not (math.isfinite(w) and 0 < w <= 500):
        missing.append("missed_calls_weekly")
    if not (math.isfinite(r) and 0 < r <= 100):
        missing.append("close_rate_pct")
    if not (math.isfinite(a) and 0 < a <= 100000):
        missing.append("avg_job_value")
    if missing:
        return {"ok": False, "error": "missing_leak_inputs", "missing": missing}, {}
    weekly = w * (r / 100) * a
    monthly = math.floor(weekly * 4.33 / 100) * 100
    result = {
        "ok": True,
        "weekly_leak": f"{math.floor(weekly):,}",
        "monthly_leak": f"{int(monthly):,}",
        "inputs_used": {"missed_calls_weekly": w, "close_rate_pct": r, "avg_job_value": a},
    }
    if source == "call_volume":
        result["inputs_used"]["call_volume"] = dvs.get("call_volume")
        result["missed_calls_weekly"] = int(round(w))
    elif source == "daily":
        result["inputs_used"]["missed_calls_daily"] = dvs.get("missed_calls_daily")
        result["missed_calls_weekly"] = int(round(w))
    patch = {"weekly_leak": result["weekly_leak"], "monthly_leak": result["monthly_leak"]}
    if source in ("call_volume", "daily"):
        patch["missed_calls_weekly"] = int(round(w))
    return result, patch
