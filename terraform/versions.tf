terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "pert-smart-transport-ciap"
      Student     = "Om Vivek Mehta"
      RollNumber  = "TYCS_25"
      PRN         = "124BTCS1021"
      Course      = "DevSecOps Lab"
      ManagedBy   = "Terraform"
    }
  }
}
