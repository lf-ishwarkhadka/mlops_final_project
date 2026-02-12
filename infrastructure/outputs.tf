output "instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.ec2.id
}

output "instance_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.ec2.public_ip
}

output "ssh_command" {
  description = "SSH command to connect to the instance"
  value       = "ssh -i ${var.key_name}.pem ubuntu@${aws_instance.ec2.public_ip}"
}

output "private_key_path" {
  description = "Path to the private key file"
  value       = "${path.module}/${var.key_name}.pem"
}
