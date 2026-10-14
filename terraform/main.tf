# Data source to fetch default VPC
data "aws_vpc" "default" {
  default = true
}

# Fetch the official Ubuntu 22.04 LTS Jammy AMI
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Least-Privilege Security Group
resource "aws_security_group" "app_sg" {
  name        = "${var.project_name}-sg"
  description = "Allow HTTP and SSH access to PERT transportation web app"
  vpc_id      = data.aws_vpc.default.id

  # Inbound HTTP (Standard Web Port 80)
  ingress {
    description = "Allow HTTP web traffic"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Inbound Port 5000 (Direct Application Port)
  ingress {
    description = "Allow Direct Application Port 5000"
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Inbound SSH (Port 22)
  ingress {
    description = "Allow administrative SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ssh_cidr]
  }

  # Outbound All Traffic (For Docker package installation and registry pulls)
  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-sg"
  }
}

# Free Tier EC2 Instance
resource "aws_instance" "web_server" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  vpc_security_group_ids = [aws_security_group.app_sg.id]

  user_data = templatefile("${path.module}/user_data.sh", {
    docker_image = var.docker_image
  })

  root_block_device {
    volume_size           = 15
    volume_type           = "gp3"
    delete_on_termination = true
    encrypted             = true
  }

  tags = {
    Name = "${var.project_name}-instance"
  }
}
