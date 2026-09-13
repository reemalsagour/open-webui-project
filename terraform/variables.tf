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