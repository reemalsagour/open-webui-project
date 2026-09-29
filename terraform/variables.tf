variable "location" {
  description = "Azure region"
  type        = string
  default     = "eastus2"
}

variable "resource_group_name" {
  description = "Azure resource group name"
  type        = string
  default     = "rg-openwebui"
}

variable "vm_name" {
  description = "Azure VM name"
  type        = string
  default     = "vm-openwebui"
}

variable "vm_size" {
  description = "Azure VM size"
  type        = string
  default     = "Standard_D4ls_v6"
}

variable "admin_username" {
  description = "Linux administrator username"
  type        = string
  default     = "azureadmin"
}

variable "ssh_public_key" {
  description = "SSH public key"
  type        = string
  sensitive   = true
}

variable "allowed_ssh_cidr" {
  description = "IP address allowed to SSH to the VM"
  type        = string
}

variable "allowed_web_cidr" {
  description = "IP address allowed to access Open WebUI"
  type        = string
}

variable "postgresql_server_name" {
  description = "Azure PostgreSQL Flexible Server name"
  type        = string
  default     = "psql-openwebui"
}

variable "postgresql_database_name" {
  description = "Open WebUI PostgreSQL database name"
  type        = string
  default     = "openwebui"
}

variable "postgresql_version" {
  description = "PostgreSQL major version"
  type        = string
  default     = "18"
}

variable "postgresql_admin_username" {
  description = "PostgreSQL administrator username"
  type        = string
  default     = "openwebuiadmin"
}

variable "postgresql_admin_password" {
  description = "PostgreSQL administrator password"
  type        = string
  sensitive   = true
}

variable "postgresql_storage_mb" {
  description = "PostgreSQL storage size in MB"
  type        = number
  default     = 32768
}

variable "postgresql_sku_name" {
  description = "PostgreSQL Flexible Server SKU"
  type        = string
  default     = "B_Standard_B1ms"
}

variable "postgresql_backup_retention_days" {
  description = "PostgreSQL backup retention period"
  type        = number
  default     = 7
}

variable "gemini_api_key" {
  description = "Google Gemini API key"
  type        = string
  sensitive   = true
}

variable "jwt_secret_key" {
  description = "JWT signing secret"
  type        = string
  sensitive   = true
}

variable "openwebui_admin_email" {
  description = "Open WebUI administrator email"
  type        = string
  default     = "admin@yourcompany.com"
}

variable "openwebui_admin_password" {
  description = "Open WebUI admin password"
  type        = string
  sensitive   = true
}

variable "key_vault_name" {
  description = "Azure Key Vault name (must be globally unique across Azure)"
  type        = string
  default     = "kv-openwebui-project"
}