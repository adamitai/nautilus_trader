terraform {
  backend "s3" {
    bucket = "nautilus-arbitrage-terraform-state-dev-us-west-2"
    key    = "terraform.tfstate"
    region = "us-west-2"
  }
}
