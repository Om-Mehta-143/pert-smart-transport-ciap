# Latest Ubuntu 22.04 LTS AMI lookup dynamically
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

resource "aws_instance" "lab_instance" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.public_subnet.id
  vpc_security_group_ids = [aws_security_group.lab_sg.id]

  user_data = <<-EOF
              #!/bin/bash
              sudo apt-get update -y
              sudo apt-get install -y ca-certificates curl gnupg unzip
              
              # Install Docker
              sudo install -m 0755 -d /etc/apt/keyrings
              curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
              sudo chmod a+r /etc/apt/keyrings/docker.gpg
              echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
              sudo apt-get update -y
              sudo apt-get install -y docker-ce docker-ce-cli containerd.io
              sudo usermod -aG docker ubuntu
              sudo systemctl enable --now docker

              # Install AWS CLI v2
              curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "/tmp/awscliv2.zip"
              unzip -q /tmp/awscliv2.zip -d /tmp
              sudo /tmp/aws/install

              # Authenticate with AWS ECR & Run Container
              export AWS_DEFAULT_REGION="${var.aws_region}"
              aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin 821302803491.dkr.ecr.${var.aws_region}.amazonaws.com || true
              docker run -d --name pert-app-prod --restart always -p 5000:5000 -p 80:5000 ${var.docker_image}
              EOF

  root_block_device {
    volume_size           = 16
    volume_type           = "gp3"
    delete_on_termination = true
  }

  tags = {
    Name = "pert-smart-transport-ec2-tf"
  }
}
