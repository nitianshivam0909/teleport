# Teleport CE PAM Portal (JIT Access)

A full PAM web portal that layers enterprise-like Just-In-Time access workflows over an existing Teleport Community Edition cluster.

## What this portal adds on top of Teleport CE

- Web-based JIT access request creation.
- Web-based admin approvals/denials.
- Multi-person approval threshold (for example, 2 approvals required).
- Slack notifications on request creation.
- Jira ticket enforcement via issue validation API.
- JWT auth and role-based workflow (`developer`, `admin`, `security`).
- Portal-level audit records.

Teleport backend is unchanged: this app orchestrates `tsh` and `tctl` commands.

## Architecture

```text
User -> React Frontend -> FastAPI Backend -> tsh/tctl CLI -> Teleport Auth Server -> SSH Node
```

## Project structure

```text
.
├── backend/
│   ├── app/
│   │   ├── auth.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── services.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/NavBar.jsx
│   │   ├── lib/api.js
│   │   ├── pages/
│   │   │   ├── AdminApprovalPage.jsx
│   │   │   ├── AuditLogsPage.jsx
│   │   │   ├── CreateRequestPage.jsx
│   │   │   ├── DashboardPage.jsx
│   │   │   └── LoginPage.jsx
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── Dockerfile
│   ├── index.html
│   ├── package.json
│   ├── postcss.config.js
│   ├── tailwind.config.js
│   └── vite.config.js
├── docker-compose.yml
├── schema.sql
└── .env.example
```

## RBAC model

- `developer`
  - Can log in
  - Can create access requests
  - Can view own requests
- `admin`
  - Can log in
  - Can create requests
  - Can approve/deny pending requests
  - Can view all requests and audit logs
- `security`
  - Can log in
  - Can view all requests and audit logs

Default seeded users (password: `changeme`):
- `dev1` (developer)
- `admin1` (admin)
- `sec1` (security)

## API endpoints

- `POST /auth/login`
- `POST /requests/create`
- `GET /requests`
- `POST /requests/{id}/approve`
- `POST /requests/{id}/deny`
- `GET /audit/logs`

## Teleport integration commands

The backend executes:

- Create request:
  - `tsh request create --roles=<role> --reason <reason> --format=json`
- Final approval when threshold met:
  - `tctl requests approve <teleport-request-id>`
- Denial:
  - `tctl requests deny <teleport-request-id>`
- (helper available) list requests:
  - `tctl requests ls --format=json`

## Multi-person approval workflow

`REQUIRED_APPROVALS` controls quorum (default `2`).

- Every admin approval is stored in `approvals`.
- When count >= threshold, backend runs `tctl requests approve`.

## Jira enforcement

When creating a request:
- User must provide `ticket_id`.
- Backend validates with:
  - `GET /rest/api/2/issue/{ticket}`
- Invalid ticket returns `400 Invalid ticket ID`.

If `JIRA_BASE_URL` is not set, validation is skipped (for local dev).

## Slack notifications

On request creation, backend posts to Slack Incoming Webhook:

```text
User: <username>
Requested Role: <role>
Server: <resource>
Reason: <reason>
Approve URL: http://localhost:5173/admin
```

## Database schema

Defined in `schema.sql` and mirrored in SQLAlchemy models:
- `users`
- `access_requests`
- `approvals`
- `audit_logs`

## Quick start (how to run)

### Prerequisites

- Docker + Docker Compose plugin.
- Teleport CLI tools on host: `tsh`, `tctl`.
- Active Teleport login context for the account used by the backend automation.

Validate on host:

```bash
which tsh && tsh version
which tctl && tctl version
```

### 1) Configure environment

```bash
cp .env.example .env
```

Edit `.env`:
- Set `JWT_SECRET`.
- Keep `REQUIRED_APPROVALS=2` (or change as needed).
- Add Slack/Jira values if you want those integrations enabled.

### 2) Ensure Teleport auth state exists on host

The backend container calls `tsh`/`tctl` and reads mounted host state:
- `~/.tsh`
- `~/.tctl`

Authenticate on host before starting stack, for example:

```bash
tsh login --proxy=<proxy-host> --auth=<connector>
# if your setup needs tctl identity/certs, initialize it as you normally do in your environment
```

### 3) Start services

```bash
docker compose up --build
```

### 4) Open apps

- Frontend: `http://localhost:5173`
- Backend API docs: `http://localhost:8000/docs`

### 5) Test login (seeded users)

Password for all defaults is `changeme`:
- `dev1` (developer)
- `admin1` (admin)
- `sec1` (security)

### 6) End-to-end flow

1. Login as `dev1` and create request with role (for example `jit-ssh`) and ticket ID.
2. Login as `admin1` and approve twice (or from two admin identities) until threshold is met.
3. Backend triggers `tctl requests approve <teleport_request_id>`.
4. Security/admin can review audit logs in UI.

### Troubleshooting

- `Command failed: ... tsh ...` or `... tctl ...`:
  - Verify host binaries exist at `/usr/local/bin/tsh` and `/usr/local/bin/tctl` (mounted into backend container).
  - Verify Teleport auth state exists in `~/.tsh` / `~/.tctl`.
- Jira rejects tickets:
  - Confirm `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN` are valid.
- Slack message not sent:
  - Confirm `SLACK_WEBHOOK_URL` is set.
- If you want to skip Jira in local testing, leave `JIRA_BASE_URL` empty.

## Security notes

- JWT-based API auth.
- Secrets via environment variables.
- Role checks enforced server-side.
- All key actions are written to `audit_logs`.

## Extending session audit summary

`access_requests` already includes fields for:
- `session_start`
- `session_end`
- `commands_executed`

You can populate these by periodically pulling Teleport session/audit events and correlating by username/request metadata.
