output "instance_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.lab_instance.public_ip
}

output "instance_public_dns" {
  description = "Public DNS name of the EC2 instance"
  value       = aws_instance.lab_instance.public_dns
}

output "app_url" {
  description = "Direct Application URL"
  value       = "http://${aws_instance.lab_instance.public_ip}:5000"
}

output "ssh_command" {
  description = "Ready-to-use SSH command"
  value       = "ssh ubuntu@${aws_instance.lab_instance.public_ip}"
}
