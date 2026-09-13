# Security Documentation

## 1. Overview

Security is an important part of the Internal AI Chat Platform.

The platform uses Azure networking controls, SSH key authentication, Docker isolation, and restricted network access.

## 2. Azure Network Security

An Azure Network Security Group (NSG) controls inbound traffic to the virtual machine.

The NSG contains rules for required administrative and application traffic.

## 3. SSH Security

SSH is provided through TCP port 22.

SSH access is restricted to the administrator's approved IP address.

Password-based SSH authentication is disabled.

SSH public-key authentication is used instead.

The SSH private key must remain on the administrator's computer and must never be committed to source control.

## 4. Open WebUI Network Access

Open WebUI is exposed through the configured application port.

Access is restricted using an Azure Network Security Group rule.

The application should not be exposed to unrestricted internet access.

## 5. Docker Network Security

Open WebUI and Ollama communicate through a Docker network.

Ollama does not need to be directly exposed to the public internet.

The Ollama service is accessed by Open WebUI through the internal Docker network.

## 6. Secrets Management

Sensitive information must not be stored directly in source code.

The following types of information must not be committed to Git:

* Passwords
* API keys
* SSH private keys
* Authentication tokens
* Terraform state containing sensitive information
* Private environment files

The project `.gitignore` file excludes sensitive configuration files.

## 7. Terraform State

Terraform state files can contain infrastructure information and may contain sensitive values.

Terraform state must therefore be protected and must not be committed to a public Git repository.

For a production environment, a secure remote Terraform backend should be considered.

## 8. Operating System Security

The Azure VM should receive regular operating system updates.

Recommended maintenance command:

```bash
sudo apt update
sudo apt upgrade
```

Security updates should be applied regularly.

## 9. Container Security

Docker containers should use trusted images and should be updated regularly.

Container logs should be reviewed when troubleshooting unexpected behavior.

## 10. AI Data Security

Users should not provide sensitive information to the AI assistant unless permitted by the organization's security policy.

Examples of information that should generally not be entered include:

* Passwords
* Authentication tokens
* Private encryption keys
* Unnecessary personal information
* Confidential information not approved for AI processing

## 11. HTTPS

The current development deployment uses the configured application endpoint.

For a production deployment, HTTPS/TLS should be implemented using a reverse proxy or another approved secure-access solution.

## 12. Future Security Improvements

Recommended improvements for a production deployment include:

* HTTPS/TLS
* Reverse proxy
* Private Azure networking
* VPN or private access
* Centralized logging
* Azure monitoring
* Stronger identity management
* Automated security updates
* Formal backup procedures
* Remote Terraform state