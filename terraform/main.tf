terraform {
  required_version = ">= 1.5.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "open_webui" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_virtual_network" "open_webui" {
  name                = "vnet-openwebui"
  address_space       = ["10.10.0.0/16"]
  location            = azurerm_resource_group.open_webui.location
  resource_group_name = azurerm_resource_group.open_webui.name
}

resource "azurerm_subnet" "open_webui" {
  name                 = "subnet-openwebui"
  resource_group_name  = azurerm_resource_group.open_webui.name
  virtual_network_name = azurerm_virtual_network.open_webui.name
  address_prefixes     = ["10.10.1.0/24"]
}

resource "azurerm_public_ip" "open_webui" {
  name                = "pip-openwebui"
  location            = azurerm_resource_group.open_webui.location
  resource_group_name = azurerm_resource_group.open_webui.name
  allocation_method   = "Static"
  sku                 = "Standard"
}

resource "azurerm_network_security_group" "open_webui" {
  name                = "nsg-openwebui"
  location            = azurerm_resource_group.open_webui.location
  resource_group_name = azurerm_resource_group.open_webui.name

  security_rule {
    name                       = "Allow-SSH"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = var.allowed_ssh_cidr
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "Allow-OpenWebUI"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "3000"
    source_address_prefix      = var.allowed_web_cidr
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "Allow-Streamlit"
    priority                   = 120
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "8501"
    source_address_prefix      = var.allowed_web_cidr
    destination_address_prefix = "*"
  }
}

resource "azurerm_network_interface" "open_webui" {
  name                = "nic-openwebui"
  location            = azurerm_resource_group.open_webui.location
  resource_group_name = azurerm_resource_group.open_webui.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.open_webui.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.open_webui.id
  }
}

resource "azurerm_network_interface_security_group_association" "open_webui" {
  network_interface_id      = azurerm_network_interface.open_webui.id
  network_security_group_id = azurerm_network_security_group.open_webui.id
}

resource "azurerm_linux_virtual_machine" "open_webui" {
  name                = var.vm_name
  resource_group_name = azurerm_resource_group.open_webui.name
  location            = azurerm_resource_group.open_webui.location
  size                = var.vm_size

  admin_username = var.admin_username

  network_interface_ids = [
    azurerm_network_interface.open_webui.id
  ]

  disable_password_authentication = true

  admin_ssh_key {
    username   = var.admin_username
    public_key = var.ssh_public_key
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "ubuntu-24_04-lts"
    sku       = "server"
    version   = "latest"
  }

  tags = {
    project     = "open-webui"
    application = "Open-WebUI"
    environment = "development"
  }

  identity {
    type = "SystemAssigned"
  }
}