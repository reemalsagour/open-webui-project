# Internal AI Chat Platform Based on OpenWebUI

## 1. Project Summary

This project is an internal AI chat platform based on OpenWebUI. It provides a centralized environment for AI conversations, document management, and organizational knowledge.

The platform consists of:

* **Streamlit** — frontend user interface
* **FastAPI** — backend API and application logic
* **OpenWebUI** — AI interaction and document/knowledge functionality
* **Gemini** — AI model provider
* **PostgreSQL** — application database (a local container for development, Azure PostgreSQL Flexible Server for deployment)
* **Docker** — containerization
* **Terraform** — Azure infrastructure provisioning
* **Azure Key Vault** — stores deployment secrets (Azure only)
* **Bash / PowerShell scripts** — setup and deployment automation

Users can start AI conversations, manage conversation history, upload documents, and create and manage knowledge bases.

---

## 2. Requirements

### Required for Local Installation

* Python 3.12+
* Docker
* Docker Compose
* Gemini API key

The local stack (`docker-compose.dev.yml`) runs its own PostgreSQL container, so a separate database install is not needed locally.

### Required for Azure Installation

* Azure account/subscription
* Azure CLI
* Terraform 1.5+
* Git and an SSH client (built into Windows 10/11 and Linux)
* SSH key pair
* Gemini API key
* **Azure permissions to create resources and role assignments** — Owner on the subscription/resource group, or Contributor plus User Access Administrator. Terraform creates a Key Vault role assignment for the VM, which Contributor alone cannot do.
* Quota for the VM size in the chosen region (default: `Standard_D4ls_v6` in `eastus2`)

PostgreSQL and Key Vault are **not** prerequisites to install yourself on Azure — Terraform creates both.

---

## 3. Installation

### 3.1 Local Installation

#### Step 1 — Create the environment file

Copy `.env.example` and rename it to `.env`:

Fill in the required values in `.env` using the [API Keys & Environment Variables](#5-api-keys--environment-variables) section below.

#### Step 2 — Start the application

Cd into the docker folder and build and start the Docker containers in dev mode:

```bash
cd docker
docker compose --env-file "../.env"  -f docker-compose.yml -f docker-compose.dev.yml up --build -d
```

The application can then be accessed through the configured addresses:
* http://localhost:8000 for backend
* http://localhost:8501 for frontend
* http://localhost:3000 for OpenWebUI (admin and testing)

---

### 3.2 Azure Installation

There are two ways to deploy to Azure: the automated script, or the manual steps.

#### Automated

From the repository root, in Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\bootstrap.ps1
```

Windows blocks scripts downloaded or copied from outside sources by default, so `-ExecutionPolicy Bypass` is required even if your PowerShell execution policy is already set to `RemoteSigned`. If preferred, running `Unblock-File -Path .\bootstrap.ps1` once removes the block permanently, after which `.\bootstrap.ps1` on its own also works.

This deploys **your own, separate copy of the infrastructure** under your own Azure subscription. It does not share or connect to a teammate's deployment. Each person who wants their own running copy runs this on their own machine, logged into their own Azure account.

The script:
1. Checks that Azure CLI, Terraform, Git, and SSH are installed
2. Logs you in to Azure and confirms the subscription
3. Creates `terraform/terraform.tfvars` the first time it runs (asks for your public IP, a PostgreSQL password, a Gemini API key, an Open WebUI admin email and password — input is hidden), and reuses it on every later run without asking again
4. Checks that PostgreSQL and the VM are running, and starts them automatically if either was stopped to save Azure credit
5. Shows the Terraform plan and asks for confirmation before applying — it stops and requires typing `DESTROY` if the plan would delete or replace anything
6. Uploads your current committed code to the VM and fixes Windows line endings automatically
7. Runs `scripts/setup.sh` on the VM, which reads secrets from Key Vault, generates `.env`, and starts the containers
8. Runs `scripts/validate.sh` and prints the URLs

To redeploy only the application code to a VM that already exists, skipping the Terraform check for a faster run:
```powershell
powershell -ExecutionPolicy Bypass -File .\bootstrap.ps1 -SkipInfra
```
Running the plain command (no flag) always works too, even for a code-only redeploy — it just re-checks Terraform every time, and reports "no changes" if nothing infrastructure-related was edited. `-SkipInfra` is an optional shortcut that skips that check entirely; it is not required.

If something goes wrong partway through, the script's own messages say what failed and what to check (see also the [Troubleshooting](#7-troubleshooting) section below).

#### Manual steps

Use this if you are not on Windows, or want to run each step yourself.

**Step 1 — Log in to Azure**
```bash
az login
```

**Step 2 — Create an SSH key pair** (skip if you already have one)
```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/openwebui_key
```

**Step 3 — Configure Terraform**
```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```
Edit `terraform.tfvars` and fill in every placeholder, including `ssh_public_key` (contents of `openwebui_key.pub`), `allowed_ssh_cidr` / `allowed_web_cidr` (your public IP, e.g. `YOUR_IP/32`), `postgresql_server_name` and `key_vault_name` (must each be globally unique across Azure), and the secret values (`postgresql_admin_password`, `gemini_api_key`, `jwt_secret_key`, `openwebui_admin_password`, `openwebui_admin_email`). `terraform.tfvars` holds real secrets — it is git-ignored and must never be committed.

Review the resources that will be created:
```bash
terraform plan
```

**Step 4 — Provision the Azure infrastructure**
```bash
terraform apply
```
Confirm when prompted. This takes 10–15 minutes, mostly for PostgreSQL. Note the outputs:
```bash
terraform output public_ip_address
terraform output postgresql_fqdn
terraform output key_vault_name
```

**Step 5 — Get the code onto the VM**
```bash
ssh -i ~/.ssh/openwebui_key azureadmin@<VM_PUBLIC_IP>
```
```bash
# on the VM
git clone https://github.com/<OWNER>/<REPO>.git ~/open-webui-project
```
A private repository asks for a username and a personal access token instead of a password.

**Step 6 — Run setup**
```bash
# on the VM
cd ~/open-webui-project/scripts
bash setup.sh <key-vault-name> <postgresql-fqdn> <admin-email>
```
This installs Docker if missing, reads secrets from Key Vault, writes `.env`, and starts the containers. **You do not create `.env` by hand on Azure** — it is generated from Key Vault.

**Step 7 — Verify**
```bash
docker compose -f ~/open-webui-project/docker/docker-compose.yml ps
bash ~/open-webui-project/scripts/validate.sh
```
The application is then reachable at:
* `http://<VM_PUBLIC_IP>:8501` for frontend
* `http://<VM_PUBLIC_IP>:3000` for OpenWebUI (admin and testing)

---

## 4. Run the Project

### Local

From the `docker` directory:

```bash
docker compose --env-file "../.env"  -f docker-compose.yml -f docker-compose.dev.yml up --build -d
```

To stop the application:

```bash
docker compose --env-file "../.env"  -f docker-compose.yml -f docker-compose.dev.yml down
```

> `down -v` also deletes local volumes, including the local development database. Only use it to reset everything.

### Azure

Re-run the deployment script any time to redeploy the latest code:
```powershell
powershell -ExecutionPolicy Bypass -File .\bootstrap.ps1 -SkipInfra
```

Or connect and use the scripts directly:
```bash
ssh -i ~/.ssh/openwebui_key azureadmin@<VM_PUBLIC_IP>
```
```bash
# on the VM
cd ~/open-webui-project/scripts
bash start.sh       # start
bash stop.sh        # stop containers (keeps them and their data)
bash cleanup.sh     # remove containers (keeps volumes and the database)
bash validate.sh    # health checks

cd ~/open-webui-project/docker
docker compose logs -f
docker compose down
```

To pause the deployment and stop Azure billing for compute between sessions:
```bash
az vm deallocate --resource-group rg-openwebui --name vm-openwebui
az postgres flexible-server stop --resource-group rg-openwebui --name <postgresql_server_name>
```
`bootstrap.ps1` detects and starts both automatically on its next run. Azure restarts a stopped PostgreSQL server on its own after 7 days if it is not started manually first.

---

## 5. API Keys & Environment Variables

Create the environment file from the provided .env.example file:

```bash
cp .env.example .env
```

On Azure, `.env` is generated automatically by `setup.sh` from Key Vault — this table is for local development and for reference.

### Where to obtain each value

| Variable                      | Purpose                           | Obtain from                                                             |
| ----------------------------- | --------------------------------- | ----------------------------------------------------------------------- |
| `POSTGRES_PASSWORD`           | PostgreSQL database password      | Your Postgres password that you use to connect to PostgreSQL in `psql`  |
| `POSTGRES_HOST`               | PostgreSQL database host          | `localhost` for local use or the Azure PostgreSQL host             |
| `POSTGRES_USER`               | PostgreSQL database user          | `openwebuiadmin`                                                        |
| `POSTGRES_DB`                 | PostgreSQL database name          | `openwebui`                                                             |
| `POSTGRES_SSL`                 | PostgreSQL SLL setting          | `require` for deployment. `disable` for local                                                              |
| `JWT_SECRET_KEY`              | Secret used to sign JWT tokens    | [JWT Secret Key Generator](https://jwtsecretkeygenerator.com/)          |
| `JWT_ALGORITHM`               | JWT signing algorithm             | `HS256`                                                                 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime                    | `1440`                                                                  |
| `GEMINI_API_KEY`              | Gemini API key                    | [Google AI Studio API Keys](https://aistudio.google.com/api-keys)       |
| `OPEN_WEB_UI_API_URL`         | Address of the OpenWebUI instance | `http://localhost:3000` for local use or the OpenWebUI address in Azure |
| `OPENWEBUI_ADMIN_EMAIL`       | OpenWebUI admin email             | Whatever email you want                                                 |
| `OPENWEBUI_ADMIN_PASSWORD`    | OpenWebUI admin password          | Whatever password you want                                              |
| `FRONTEND_TEST_MODE`    | For front end to use test mode or real backend          | `false`                                              |
| `BACKEND_URL`    | Backend URL that the frontend should use          | http://localhost:8000                                              |

On Azure, three additional values are set automatically and are **not** part of `.env.example`:
* `POSTGRES_USER`, `POSTGRES_DB` — fixed to `openwebuiadmin` / `openwebui` by `setup.sh`
* `OPEN_WEB_UI_API_KEY` — generated automatically at startup and shared with the backend through a Docker volume, not read from `.env`

---

## 6. Security

* **Never commit** `.env`, `terraform.tfvars`, `*.tfstate`, `tfplan`, or private SSH keys. `.gitignore` covers these — check `git status` before every commit.
* Terraform state stores secret values in plain text. Keep `terraform.tfstate` private.
* PostgreSQL on Azure has public access disabled and is reachable only from inside the virtual network.
* Secrets live in Azure Key Vault; the VM reads them through a managed identity, so no credentials are needed to fetch them.
* The VM accepts SSH keys only — password login is disabled.
* Restrict `allowed_ssh_cidr` and `allowed_web_cidr` to known addresses instead of `0.0.0.0/0`.
* HTTPS is not configured. Avoid entering sensitive data until a domain and certificate are added.

---

## 7. Troubleshooting

| Problem | Cause and fix |
|---|---|
| `$'\r': command not found` or `exec ...sh: no such file or directory` on the VM | Windows line endings in a shell script. `bootstrap.ps1` fixes this automatically on upload; if editing directly on the VM, run `sed -i 's/\r$//' <file>`. |
| `The "X" variable is not set. Defaulting to a blank string` | Docker Compose reads `.env` from the same folder as the compose file. Run with `--env-file ../.env`, or on the VM confirm the symlink exists: `ls -la ~/open-webui-project/docker/.env`. |
| `terraform plan` fails with a `ServerStoppedError` on PostgreSQL | The database was stopped to save credit. `bootstrap.ps1` starts it automatically; manually: `az postgres flexible-server start --resource-group rg-openwebui --name <name>`. |
| SSH hangs or times out | Either the VM is stopped (`az vm start --resource-group rg-openwebui --name vm-openwebui`), or your public IP no longer matches `allowed_ssh_cidr` in `terraform.tfvars` — check with `(Invoke-RestMethod https://api.ipify.org)` and update + re-apply if it changed. |
| `REMOTE HOST IDENTIFICATION HAS CHANGED` | The VM was recreated and has a new host key. Run `ssh-keygen -R <VM_IP>` and reconnect. |
| Logging into OpenWebUI fails with the email you expected | The admin account is only created on the **first ever** boot of OpenWebUI. Changing `OPENWEBUI_ADMIN_EMAIL`/`PASSWORD` later does not change an account that already exists — use the original credentials, or reset by removing the `open-webui-data` and `open-webui-api-key` volumes (this deletes existing OpenWebUI accounts, settings, and chat history). |
| `setup-openwebui` fails with HTTP 400 on login | Leftover, mismatched admin credentials or a stale cached API key. Reset both volumes (see above), then restart. |
| Terraform wants to replace the VM | Changing `ssh_public_key` on an existing deployment can force VM replacement, which wipes local files. `bootstrap.ps1` shows the plan and requires typing `DESTROY` before applying anything destructive — read it carefully. |
| `terraform destroy` refuses to delete the database | `prevent_destroy` is set on the database resource on purpose. Remove that block in `postgresql.tf` first if a full teardown is intended. |

---

## 8. Known Issues

* Gemini availability depends on the external Gemini API and its service limits.
* Gemini model names may change over time, which may require updating the configured model names.
* Temporary errors or high demand from the external AI service may affect AI responses.
* OpenWebUI's own accounts, settings, and any chats made directly in its interface (port 3000) are stored in its own Docker volume, not in PostgreSQL, and are not recorded by the backend.
* Uploaded documents are stored in a Docker volume on the VM; recreating the VM removes them.
* `.env` on the Azure VM is plain text once generated from Key Vault; the applications do not read secrets from Key Vault directly at runtime.
* Each deployment is independent and tied to a single Azure subscription — there is no shared or multi-user setup yet.
