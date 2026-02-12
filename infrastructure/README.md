# EC2 Instance with Docker Setup

Terraform configuration to provision an EC2 instance with Docker and Docker Compose pre-installed.

## Prerequisites

- Terraform >= 1.0
- AWS CLI configured with credentials
- AWS account with appropriate permissions

## Configuration

Update `terraform.tfvars` with your desired values:

```hcl
aws_region    = "us-east-1"
instance_type = "t3.medium"
key_name      = "ishwar_samir_mlops_key"
ami_id        = "ami-0e2c8caa4b6378d8c"  # Ubuntu 24.04 LTS
```

## Usage

1. Initialize Terraform:
```bash
terraform init
```

2. Review the execution plan:
```bash
terraform plan
```

3. Apply the configuration:
```bash
terraform apply
```

4. Get the SSH command from outputs:
```bash
terraform output ssh_command
```

## Connecting to EC2

After applying, use the generated private key to SSH:

```bash
chmod 400 ishwar_samir_mlops_key.pem
ssh -i ishwar_samir_mlops_key.pem ubuntu@<instance-public-ip>
```

## Docker Installation

Docker and Docker Compose are automatically installed via user data script. The installation runs in the background during first boot and may take 3-5 minutes.

### Check Installation Status

After SSH into the instance:

```bash
# Check if user data script is still running
ps aux | grep apt

# View user data execution logs
sudo cat /var/log/cloud-init-output.log

# Check for errors
sudo tail -100 /var/log/cloud-init.log
```

### Verify Docker Installation

```bash
docker --version
docker compose version
```

**Note:** If you get "permission denied", log out and log back in for the docker group membership to take effect.

## Resources Created

- EC2 instance (t3.medium, Ubuntu 24.04, 50GB storage)
- Security group allowing SSH from anywhere (0.0.0.0/0)
- SSH key pair
- Private key file (.pem)

## Security Warning

The security group allows SSH access from any IP (0.0.0.0/0). For production use, restrict this to your specific IP:

```hcl
cidr_ipv4 = "YOUR_IP/32"
```

## Cleanup

To destroy all resources:

```bash
terraform destroy
```

## Outputs

- `instance_id`: EC2 instance ID
- `instance_public_ip`: Public IP address
- `ssh_command`: Ready-to-use SSH command
- `private_key_path`: Path to the private key file
