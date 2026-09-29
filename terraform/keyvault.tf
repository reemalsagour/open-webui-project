data "azurerm_client_config" "current" {}

resource "azurerm_key_vault" "open_webui" {
  name                       = var.key_vault_name
  resource_group_name        = azurerm_resource_group.open_webui.name
  location                   = azurerm_resource_group.open_webui.location
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  purge_protection_enabled   = false
  soft_delete_retention_days = 7
  rbac_authorization_enabled = true
}

resource "azurerm_role_assignment" "terraform_keyvault_admin" {
  scope                = azurerm_key_vault.open_webui.id
  role_definition_name = "Key Vault Administrator"
  principal_id          = data.azurerm_client_config.current.object_id
}

resource "azurerm_role_assignment" "vm_keyvault_reader" {
  scope                = azurerm_key_vault.open_webui.id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azurerm_linux_virtual_machine.open_webui.identity[0].principal_id
  depends_on = [azurerm_role_assignment.terraform_keyvault_admin]
}

resource "azurerm_key_vault_secret" "postgres_password" {
  name         = "postgres-password"
  value        = var.postgresql_admin_password
  key_vault_id = azurerm_key_vault.open_webui.id
  depends_on   = [azurerm_role_assignment.terraform_keyvault_admin]
}

resource "azurerm_key_vault_secret" "gemini_api_key" {
  name         = "gemini-api-key"
  value        = var.gemini_api_key
  key_vault_id = azurerm_key_vault.open_webui.id
  depends_on   = [azurerm_role_assignment.terraform_keyvault_admin]
}

resource "azurerm_key_vault_secret" "jwt_secret_key" {
  name         = "jwt-secret-key"
  value        = var.jwt_secret_key
  key_vault_id = azurerm_key_vault.open_webui.id
  depends_on   = [azurerm_role_assignment.terraform_keyvault_admin]
}

resource "azurerm_key_vault_secret" "openwebui_admin_password" {
  name         = "openwebui-admin-password"
  value        = var.openwebui_admin_password
  key_vault_id = azurerm_key_vault.open_webui.id
  depends_on   = [azurerm_role_assignment.terraform_keyvault_admin]
}