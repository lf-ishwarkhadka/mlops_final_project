# CI/CD Setup Instructions

## Prerequisites

1. **EC2 Instance Setup:**
   - Ubuntu 22.04 or later
   - Docker and Docker Compose installed
   - Ports 22 (SSH), 80, 8000, 6333 open in security group
   - At least t3.medium (2 vCPU, 4GB RAM)

2. **Install Docker on EC2:**
   ```bash
   sudo apt update
   sudo apt install -y docker.io docker-compose-plugin
   sudo systemctl enable docker
   sudo systemctl start docker
   
   # Add your user to docker group
   sudo usermod -aG docker $USER
   newgrp docker
   ```

3. **Create app directory on EC2:**
   ```bash
   mkdir -p ~/app
   ```

## GitHub Secrets Configuration

Go to your repository → Settings → Secrets and variables → Actions → New repository secret

Add the following secrets:

- **EC2_IP**: Your EC2 instance public IP address (e.g., `54.123.45.67`)
- **EC2_USER**: SSH username (usually `ubuntu` for Ubuntu AMI, `ec2-user` for Amazon Linux)
- **SSH_PRIVATE_KEY**: Your EC2 private key (the entire content of your .pem file)

### How to add SSH_PRIVATE_KEY:
```bash
# On your local machine, copy the private key content
cat ~/path/to/your-key.pem
# Copy the entire output including -----BEGIN RSA PRIVATE KEY----- and -----END RSA PRIVATE KEY-----
# Paste it as the value for SSH_PRIVATE_KEY secret
```

## Deployment

### Automatic Deployment
Push to `main` branch triggers automatic deployment:
```bash
git add .
git commit -m "Deploy changes"
git push origin main
```

### Manual Deployment
Go to Actions tab → Deploy to EC2 → Run workflow

## Access Your Application

After successful deployment:

- **Frontend**: http://YOUR_EC2_IP
- **Backend API**: http://YOUR_EC2_IP:8000
- **API Documentation**: http://YOUR_EC2_IP:8000/docs
- **Qdrant Dashboard**: http://YOUR_EC2_IP:6333/dashboard

## Local Development

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Update `.env` with your values:
   ```
   EC2_IP=localhost
   BACKEND_PORT=8000
   FRONTEND_PORT=8501
   ```

3. Run locally:
   ```bash
   docker compose up --build
   ```

## Troubleshooting

### SSH connection issues:
```bash
# Test SSH connection locally
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# Check EC2 security group allows SSH from GitHub Actions IPs
# Or allow from 0.0.0.0/0 (less secure but simpler)
```

### Check deployment on EC2:
```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
cd ~/app
docker compose logs -f
```

### View deployment logs:
```bash
docker compose logs -f
```

### Restart services:
```bash
docker compose restart
```

### Check container health:
```bash
docker compose ps
curl http://localhost:8000/health
```

## Security Recommendations

1. Use HTTPS (add Nginx with Let's Encrypt)
2. Restrict EC2 security group to specific IPs
3. Use AWS Secrets Manager for sensitive data
4. Enable CloudWatch logging
5. Regular security updates: `sudo apt update && sudo apt upgrade`
