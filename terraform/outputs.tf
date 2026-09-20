output "resource_group_name" {
  value = azurerm_resource_group.open_webui.name
}

output "vm_name" {
  value = azurerm_linux_virtual_machine.open_webui.name
}

output "public_ip_address" {
  value = azurerm_public_ip.open_webui.ip_address
}

output "ssh_command" {
  value = "ssh ${var.admin_username}@${azurerm_public_ip.open_webui.ip_address}"
}

output "open_webui_url" {
  value = "http://${azurerm_public_ip.open_webui.ip_address}:3000"
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
