variable "aws_region" {
  description = "AWS deployment region (Free Tier enabled)"
  type        = string
  default     = "ap-south-1" # Mumbai
}

variable "instance_type" {
  description = "EC2 instance size adhering to AWS Free Tier"
  type        = string
  default     = "t3.micro"
}

variable "project_name" {
  description = "Unique project identifier tag"
  type        = string
  default     = "pert-smart-transport-ciap"
}

variable "docker_image" {
  description = "Container image tag from Docker Hub"
  type        = string
  default     = "jinwooarise/pert-smart-transport-ciap:latest"
}

variable "allowed_ssh_cidr" {
  description = "CIDR block permitted for SSH access (restricted to operator IP for least privilege)"
  type        = string
  default     = "0.0.0.0/0" # In production, restrict to your public IP e.g. 103.x.x.x/32
}
