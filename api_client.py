"""CrewAI Enterprise API client for kicking off crews and polling results."""

import time

import requests

REQUEST_TIMEOUT = 30  # seconds per HTTP request

# Documented states: "running", "completed", "error"
# Observed from actual API: "STARTED", "SUCCESS" (case varies)
# We normalize to lowercase and map to a canonical set.
DONE_STATES = {"completed", "success"}
RUNNING_STATES = {"running", "started", "pending"}
ERROR_STATES = {"error", "failed"}


def kickoff_crew(base_url: str, token: str, inputs: dict) -> str:
    """POST to /kickoff and return the kickoff_id."""
    resp = requests.post(
        f"{base_url.rstrip('/')}/kickoff",
        json={"inputs": inputs},
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()["kickoff_id"]


def poll_status(base_url: str, token: str, kickoff_id: str) -> dict:
    """GET /{kickoff_id}/status and return {"state": ..., "result": ...}."""
    resp = requests.get(
        f"{base_url.rstrip('/')}/status/{kickoff_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    data = resp.json()

    # API may use "state" or "status" as the field name
    raw_state = data.get("state") or data.get("status") or "unknown"
    state = raw_state.lower()
    result = None

    if state in DONE_STATES:
        # Documented: {"result": {"output": "...", "tasks": [...]}}
        # Also handle: {"result": "..."} or {"final_output": "..."}
        raw_result = data.get("result") or data.get("final_output") or ""
        if isinstance(raw_result, dict):
            result = raw_result.get("output") or raw_result.get("summary") or str(raw_result)
        else:
            result = str(raw_result)

    return {"state": state, "result": result}


def run_crew_and_wait(
    base_url: str,
    token: str,
    inputs: dict,
    poll_interval: float = 5.0,
    timeout: float = 300.0,
) -> str:
    """Kick off a crew, poll until complete, and return the final output text.

    Raises TimeoutError after `timeout` seconds.
    Raises RuntimeError on error states or unexpected states.
    """
    kickoff_id = kickoff_crew(base_url, token, inputs)

    interval = poll_interval
    elapsed = 0.0

    while elapsed < timeout:
        time.sleep(interval)
        elapsed += interval

        status = poll_status(base_url, token, kickoff_id)

        if status["state"] in DONE_STATES:
            return status["result"] or ""

        if status["state"] in ERROR_STATES:
            raise RuntimeError(
                f"Crew execution failed (kickoff_id: {kickoff_id})"
            )

        if status["state"] not in RUNNING_STATES:
            raise RuntimeError(
                f"Crew entered unexpected state: {status['state']}"
            )

        # Gentle backoff: grow 20% per poll, cap at 15s
        interval = min(interval * 1.2, 15.0)

    raise TimeoutError(
        f"Crew did not complete within {timeout} seconds (kickoff_id: {kickoff_id})"
    )
