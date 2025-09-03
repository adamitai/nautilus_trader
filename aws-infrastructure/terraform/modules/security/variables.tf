# Security Module Variables

variable "name_prefix" {
  description = "Name prefix for resources"
  type        = string
}

variable "vpc_id" {
  description = "ID of the VPC"
  type        = string
}

variable "kms_key_id" {
  description = "KMS key ID for encryption"
  type        = string
}

variable "alert_email" {
  description = "Email address for alerts"
  type        = string
  default     = ""
}

# API Keys
variable "binance_api_key" {
  description = "Binance API key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "binance_api_secret" {
  description = "Binance API secret"
  type        = string
  sensitive   = true
  default     = ""
}

variable "bybit_api_key" {
  description = "Bybit API key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "bybit_api_secret" {
  description = "Bybit API secret"
  type        = string
  sensitive   = true
  default     = ""
}

variable "okx_api_key" {
  description = "OKX API key"
  type        = string
  sensitive   = true
  default     = ""
}

variable "okx_api_secret" {
  description = "OKX API secret"
  type        = string
  sensitive   = true
  default     = ""
}

variable "okx_passphrase" {
  description = "OKX passphrase"
  type        = string
  sensitive   = true
  default     = ""
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
