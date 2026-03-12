import json
import os
import requests
import subprocess
from fastapi import HTTPException


def run_cmd(command: list[str]) -> str:
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as exc:
        raise HTTPException(status_code=500, detail=f"Command failed: {exc.stderr.strip()}") from exc


def create_teleport_request(role: str, reason: str) -> str:
    output = run_cmd(["tsh", "request", "create", f"--roles={role}", "--reason", reason, "--format=json"])
    parsed = json.loads(output)
    req_id = parsed[0].get("id") if isinstance(parsed, list) and parsed else parsed.get("id")
    if not req_id:
        raise HTTPException(status_code=500, detail="Unable to parse Teleport request id")
    return req_id


def approve_teleport_request(request_id: str) -> None:
    run_cmd(["tctl", "requests", "approve", request_id])


def deny_teleport_request(request_id: str) -> None:
    run_cmd(["tctl", "requests", "deny", request_id])


def list_teleport_requests() -> str:
    return run_cmd(["tctl", "requests", "ls", "--format=json"])


def validate_ticket(ticket_id: str) -> bool:
    jira_base = os.getenv("JIRA_BASE_URL")
    jira_email = os.getenv("JIRA_EMAIL")
    jira_token = os.getenv("JIRA_API_TOKEN")
    if not jira_base:
        return True
    if not jira_email or not jira_token:
        raise HTTPException(status_code=500, detail="Jira credentials not configured")
    url = f"{jira_base.rstrip('/')}/rest/api/2/issue/{ticket_id}"
    response = requests.get(url, auth=(jira_email, jira_token), timeout=10)
    return response.status_code == 200


def send_slack_notification(message: str) -> None:
    webhook = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook:
        return
    requests.post(webhook, json={"text": message}, timeout=10)
