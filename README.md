# Internal AI Chat Platform Based on OpenWebUI

## 1. Project Summary

This project is an internal AI chat platform based on OpenWebUI. It provides a centralized environment for AI conversations, document management, and organizational knowledge.

The platform consists of:

* **Streamlit** — frontend user interface
* **FastAPI** — backend API and application logic
* **OpenWebUI** — AI interaction and document/knowledge functionality
* **Gemini** — AI model provider
* **PostgreSQL** — application database
* **Docker** — containerization
* **Terraform** — Azure infrastructure provisioning
* **Bash scripts** — setup and deployment automation

Users can start AI conversations, manage conversation history, upload documents, and create and manage knowledge bases.

---

## 2. Requirements

### Required for Local Installation

* Python 3.12+
* Docker
* Docker Compose
* PostgreSQL
* Gemini API key

### Required for Azure Installation

* Azure account/subscription
* Azure CLI
* Terraform
* Docker
* Docker Compose
* SSH key pair
* Gemini API key
* PostgreSQL database
* Azure permissions to create and manage the required resources

---

## 3. Installation

### 3.1 Local Installation

#### Step 1 — Create the environment file

Copy `.env.example` and rename it to `.env`:

Fill in the required values in .env using the [API Keys & Environment Variables](#5-api-keys--environment-variables) section below.

#### Step 2 — Start the application

Cd into the docker folder and build and start the Docker containers in dev mode:

```bash
cd docker
docker compose --env-file "../.env"  -f docker-compose.yml -f docker-compose.dev.yml up --build -d
```

The application can then be accessed through the configured addresses:
* http://localhost:8000 for backend
* http://localhost:8501 for frontend

---

### 3.2 Azure Installation (PLACEHOLDER)

#### Step 1 — Log in to Azure

```bash
az login
```

#### Step 2 — Initialize Terraform

Navigate to the Terraform directory:

```bash
cd terraform
```

Initialize Terraform:

```bash
terraform init
```

#### Step 3 — Configure Terraform

Create the required Terraform variables file according to the provided example and enter the required Azure values.

Then review the resources that will be created:

```bash
terraform plan
```

#### Step 4 — Provision the Azure infrastructure

```bash
terraform apply
```

Confirm the operation when prompted.

#### Step 5 — Connect to the Azure VM

After Terraform finishes, connect to the provisioned VM using SSH:

```bash
ssh <username>@<VM_PUBLIC_IP>
```

#### Step 6 — Configure the application

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Enter the required environment variables.

For Azure, use the Azure PostgreSQL host for `POSTGRES_HOST`.

#### Step 7 — Start the application

Build and start the Docker containers:

```bash
docker compose up --build -d
```

Check the running containers:

```bash
docker compose ps
```

The application can then be accessed using the public address of the Azure deployment.

---

## 4. Run the Project

### Local

From the docker directory:

```bash
docker compose --env-file "../.env"  -f docker-compose.yml -f docker-compose.dev.yml up --build -d
```

To stop the application:

```bash
docker compose --env-file "../.env"  -f docker-compose.yml -f docker-compose.dev.yml down
```

### Azure (PLACEHOLDER)

Connect to the Azure VM:

```bash
ssh <username>@<VM_PUBLIC_IP>
```

Then start the application:

```bash
docker compose up -d
```

To view the logs:

```bash
docker compose logs -f
```

To stop the application:

```bash
docker compose down
```
---

## 5. API Keys & Environment Variables

Create the environment file from the provided .env.example file:

```bash
cp .env.example .env
```

The following values are required:

### Where to obtain each value

| Variable                      | Purpose                           | Obtain from                                                             |
| ----------------------------- | --------------------------------- | ----------------------------------------------------------------------- |
| `POSTGRES_PASSWORD`           | PostgreSQL database password      | Your Postgres password that you use to connect to PostgreSQL in `psql`  |
| `POSTGRES_HOST`               | PostgreSQL database host          | `localhost:5432` for local use or the Azure PostgreSQL host             |
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

---

## 6. Known Issues

* Gemini availability depends on the external Gemini API and its service limits.
* Gemini model names may change over time, which may require updating the configured model names.
* Temporary errors or high demand from the external AI service may affect AI responses.
