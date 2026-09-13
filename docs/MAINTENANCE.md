# Maintenance Guide

## 1. Starting the Platform

SSH into the Azure virtual machine.

Then run:

```bash
cd ~/open-webui-project/scripts
./start.sh
```

## 2. Stopping the Platform

Run:

```bash
cd ~/open-webui-project/scripts
./stop.sh
```

## 3. Validating the Platform

Run:

```bash
cd ~/open-webui-project/scripts
./validate.sh
```

The validation script checks:

* Docker
* Docker Compose
* Open WebUI
* Ollama
* Installed AI models
* Application health

## 4. Checking Containers

Run:

```bash
cd ~/open-webui-project/docker
docker compose ps
```

## 5. Viewing Open WebUI Logs

Run:

```bash
docker logs open-webui
```

To continuously follow the logs:

```bash
docker logs -f open-webui
```

## 6. Viewing Ollama Logs

Run:

```bash
docker logs ollama
```

## 7. Checking the AI Model

Run:

```bash
docker exec ollama ollama list
```

The expected model is:

```text
llama3.2:3b
```

## 8. Updating Docker Images

Move to the Docker directory:

```bash
cd ~/open-webui-project/docker
```

Pull the latest images:

```bash
docker compose pull
```

Restart the application:

```bash
docker compose up -d
```

## 9. Restarting the Application

Run:

```bash
cd ~/open-webui-project/scripts
./stop.sh
./start.sh
```

Then validate:

```bash
./validate.sh
```

## 10. Application Cleanup

To remove the application containers while preserving persistent Docker volumes:

```bash
cd ~/open-webui-project/scripts
./cleanup.sh
```

The persistent Docker volumes are not removed by the cleanup script.

## 11. Azure VM Management

The Azure VM should be stopped or deallocated when it is not required for testing.

This helps reduce Azure compute costs.

Example from the administrator's computer:

```bash
az vm deallocate \
  --resource-group rg-openwebui \
  --name vm-openwebui
```

To start it again:

```bash
az vm start \
  --resource-group rg-openwebui \
  --name vm-openwebui
```

## 12. Troubleshooting Open WebUI

Check the container:

```bash
docker compose ps
```

Check the logs:

```bash
docker logs open-webui
```

Restart the application:

```bash
cd ~/open-webui-project/scripts
./start.sh
```

## 13. Troubleshooting Ollama

Check the container:

```bash
docker ps
```

Check Ollama logs:

```bash
docker logs ollama
```

Check installed models:

```bash
docker exec ollama ollama list
```

## 14. Troubleshooting Docker Compose

Move to:

```bash
cd ~/open-webui-project/docker
```

Check the configuration:

```bash
docker compose config
```

Check the running services:

```bash
docker compose ps
```

## 15. Backup Considerations

Open WebUI application data and Ollama model data are stored in Docker volumes.

A production deployment should implement a formal backup strategy.

## 16. Security Maintenance

Administrators should regularly:

* Apply Ubuntu security updates
* Update Docker images
* Review application logs
* Review Azure NSG rules
* Verify SSH access restrictions
* Check Azure resource usage and costs
* Review user access

## 17. Cost Management

The Azure VM incurs compute costs while running.

When the platform is not required for testing or demonstration, deallocate the VM.

Before deleting Azure infrastructure, verify that no required data or resources will be lost.