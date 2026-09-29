output "resource_group_name" {
  description = "Azure resource group name"
  value = azurerm_resource_group.open_webui.name
}

output "vm_name" {
  description = "Azure Linux virtual machine name"
  value = azurerm_linux_virtual_machine.open_webui.name
}

output "public_ip_address" {
  description = "Public IP address of the Open WebUI VM"
  value = azurerm_public_ip.open_webui.ip_address
}

output "ssh_command" {
  description = "SSH command for connecting to the Open WebUI VM"
  value = "ssh ${var.admin_username}@${azurerm_public_ip.open_webui.ip_address}"
}

output "open_webui_url" {
  description = "URL for accessing Open WebUI"
  value = "http://${azurerm_public_ip.open_webui.ip_address}:3000"
}

output "openwebui_admin_email" {
  description = "Open WebUI administrator email"
  value       = var.openwebui_admin_email
}

output "postgresql_server_name" {
  description = "PostgreSQL Flexible Server name"
  value       = azurerm_postgresql_flexible_server.open_webui.name
}

output "postgresql_fqdn" {
  description = "PostgreSQL Flexible Server FQDN"
  value       = azurerm_postgresql_flexible_server.open_webui.fqdn
}

output "postgresql_database_name" {
  description = "Open WebUI PostgreSQL database name"
  value       = azurerm_postgresql_flexible_server_database.open_webui.name
}

output "postgresql_admin_username" {
  description = "PostgreSQL administrator username"
  value       = var.postgresql_admin_username
}

output "open_webui_postgresql_host" {
  description = "PostgreSQL hostname for Open WebUI"
  value       = azurerm_postgresql_flexible_server.open_webui.fqdn
}

output "key_vault_name" {
  description = "Azure Key Vault name"
  value       = azurerm_key_vault.open_webui.name
}