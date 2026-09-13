# Project #10 — Internal AI Chat Platform

## 1. Project Overview

This project implements an internal AI chat platform based on Open WebUI.

The platform is deployed on Microsoft Azure using Terraform for infrastructure provisioning and Docker Compose for application deployment.

The AI model is hosted locally on the Azure virtual machine using Ollama.

## 2. Technology Stack

* Microsoft Azure
* Terraform
* Ubuntu Linux
* Docker
* Docker Compose
* Open WebUI
* Ollama
* Llama 3.2 3B

## 3. Architecture

The platform follows this architecture:

Employee Browser
|
v
Azure Virtual Machine
|
v
Open WebUI
|
v
Ollama
|
v
Llama 3.2 3B

Terraform provisions the Azure infrastructure.

Docker Compose runs Open WebUI and Ollama.

Ollama provides the Llama 3.2 3B language model.

## 4. Azure Infrastructure

Terraform provisions the following Azure resources:

* Resource Group
* Virtual Network
* Subnet
* Public IP Address
* Network Security Group
* Network Interface
* Ubuntu Linux Virtual Machine

## 5. Application Components

### Open WebUI

Open WebUI provides the web-based chat interface used by employees.

### Ollama

Ollama provides the local AI model runtime.

### Llama 3.2 3B

Llama 3.2 3B is the language model used by the platform.

## 6. Project Structure

```text
open-webui-project/
│
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── terraform.tfvars
│
├── docker/
│   └── compose.yml
│
├── scripts/
│   ├── setup.sh
│   ├── start.sh
│   ├── stop.sh
│   ├── validate.sh
│   └── cleanup.sh
│
├── docs/
│   ├── USER-GUIDE.md
│   ├── SECURITY.md
│   └── MAINTENANCE.md
│
├── README.md
└── .gitignore
```

## 7. Deployment Process

The infrastructure is created using Terraform.

The application is deployed using Docker Compose.

The general deployment process is:

1. Provision Azure infrastructure using Terraform.
2. Connect to the Azure Linux virtual machine using SSH.
3. Install Docker and Docker Compose.
4. Deploy Open WebUI and Ollama using Docker Compose.
5. Download the Llama 3.2 3B model.
6. Access Open WebUI through the configured network endpoint.
7. Validate the platform using the validation script.

## 8. Operational Scripts

The project contains Bash scripts for common administrative tasks.

### setup.sh

Prepares the system and starts the application.

### start.sh

Starts Open WebUI and Ollama.

### stop.sh

Stops Open WebUI and Ollama.

### validate.sh

Checks Docker, Docker Compose, containers, Ollama models, and Open WebUI health.

### cleanup.sh

Stops and removes application containers while preserving persistent Docker volumes.

## 9. Validation

The platform can be validated using:

```bash
./validate.sh
```

The validation checks:

* Docker installation
* Docker Compose installation
* Container status
* Ollama model availability
* Open WebUI health

## 10. Security

The Azure Network Security Group restricts inbound access.

SSH access is restricted to the administrator's approved IP address.

Open WebUI access is restricted using an IP-based network security rule.

SSH password authentication is disabled and SSH public-key authentication is used.

Sensitive files such as Terraform variables, Terraform state, environment files, and SSH private keys are excluded from Git.

## 11. Persistent Storage

Docker volumes are used to persist:

* Open WebUI application data
* Ollama model data

This allows the application containers to be recreated without automatically losing the stored application data and downloaded model.

## 12. Current Status

The Azure infrastructure has been provisioned using Terraform.

Open WebUI and Ollama have been deployed using Docker Compose.

Llama 3.2 3B has been downloaded and tested.

The platform is operational and accessible through the configured Azure endpoint.