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