variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "ap-southeast-2"
}

variable "key_name" {
  description = "Name of an existing EC2 key pair to attach to the instance"
  type        = string
  default     = ""
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "vpc_cidr" {
  description = "CIDR block for the lab VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  description = "CIDR block for the public subnet"
  type        = string
  default     = "10.0.1.0/24"
}

variable "ssh_source_cidr" {
  description = "CIDR allowed to SSH into the instance"
  type        = string
  default     = "0.0.0.0/0"
}

variable "docker_image" {
  description = "Container image URI from AWS ECR"
  type        = string
  default     = "821302803491.dkr.ecr.ap-southeast-2.amazonaws.com/pert-smart-transport-ciap:latest"
}
