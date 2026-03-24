terraform {
  required_providers {
    aws = {
        source = "hashicorp/aws"
        version = "6.35.1"
    }

    tls = {
      source = "hashicorp/tls"
      version = "4.2.1"
    }

  }
}

provider "aws" {
    region = "ap-south-1"
}

provider "tls" {}