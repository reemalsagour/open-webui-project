resource "azurerm_subnet" "postgresql" {
  name                 = "snet-postgresql"
  resource_group_name  = azurerm_resource_group.open_webui.name
  virtual_network_name = azurerm_virtual_network.open_webui.name

  address_prefixes = ["10.10.2.0/24"]

  delegation {
    name = "postgresql-delegation"

    service_delegation {
      name = "Microsoft.DBforPostgreSQL/flexibleServers"

      actions = [
        "Microsoft.Network/virtualNetworks/subnets/join/action"
      ]
    }
  }
}

resource "azurerm_private_dns_zone" "postgresql" {
  name                = "openwebui.postgres.database.azure.com"
  resource_group_name = azurerm_resource_group.open_webui.name
}

resource "azurerm_private_dns_zone_virtual_network_link" "postgresql" {
  name                  = "openwebui-postgresql-dns-link"
  resource_group_name   = azurerm_resource_group.open_webui.name
  private_dns_zone_name = azurerm_private_dns_zone.postgresql.name
  virtual_network_id    = azurerm_virtual_network.open_webui.id
}

resource "azurerm_postgresql_flexible_server" "open_webui" {
  name                = var.postgresql_server_name
  resource_group_name = azurerm_resource_group.open_webui.name
  location            = azurerm_resource_group.open_webui.location
  zone = "2"

  version = var.postgresql_version

  delegated_subnet_id = azurerm_subnet.postgresql.id
  private_dns_zone_id = azurerm_private_dns_zone.postgresql.id

  administrator_login    = var.postgresql_admin_username
  administrator_password = var.postgresql_admin_password

  storage_mb = var.postgresql_storage_mb

  sku_name = var.postgresql_sku_name

  backup_retention_days = var.postgresql_backup_retention_days

  public_network_access_enabled = false

  depends_on = [
    azurerm_private_dns_zone_virtual_network_link.postgresql
  ]
}

resource "azurerm_postgresql_flexible_server_database" "open_webui" {
  name      = var.postgresql_database_name
  server_id = azurerm_postgresql_flexible_server.open_webui.id

  charset   = "UTF8"
  collation = "en_US.utf8"

  lifecycle {
    prevent_destroy = true
  }
}