output "instance_id" {
  description = "EC2 Instance ID"
  value       = aws_instance.web_server.id
}

output "instance_public_ip" {
  description = "Public IPv4 address assigned to the EC2 web instance"
  value       = aws_instance.web_server.public_ip
}

output "application_url" {
  description = "Direct web application URL (HTTP port 80)"
  value       = "http://${aws_instance.web_server.public_ip}"
}

output "application_direct_port_url" {
  description = "Direct application URL (Port 5000)"
  value       = "http://${aws_instance.web_server.public_ip}:5000"
}
