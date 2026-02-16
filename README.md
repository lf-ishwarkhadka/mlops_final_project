# MLOps RAG Project

A production-ready Retrieval-Augmented Generation (RAG) system with self-hosted models, deployed on AWS EC2 with automated CI/CD.

## Architecture

- **Backend**: FastAPI with self-hosted embedding (BGE) and LLM (Qwen2) models
- **Frontend**: Streamlit UI for document upload and chat
- **Vector Database**: Qdrant for semantic search
- **Infrastructure**: AWS EC2 with Terraform
- **CI/CD**: GitHub Actions with Docker Hub registry

## Quick Start - Local Development

### Prerequisites
- Python 3.11+
- uv package manager
- Docker and Docker Compose

### Setup

1. **Install uv:**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Clone and setup:**
   ```bash
   git clone https://github.com/your-username/mlops_final_project.git
   cd mlops_final_project
   
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -r backend/requirements.txt
   uv pip install -r frontend/requirements.txt
   ```

3. **Run with Docker:**
   ```bash
   docker compose up --build
   ```

4. **Access:**
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000/docs
   - Qdrant: http://localhost:6333/dashboard

## Production Deployment on AWS EC2

### Step 1: Provision Infrastructure with Terraform

1. **Configure AWS credentials:**
   ```bash
   export AWS_ACCESS_KEY_ID="your-access-key"
   export AWS_SECRET_ACCESS_KEY="your-secret-key"
   export AWS_DEFAULT_REGION="us-east-1"
   ```

2. **Update Terraform variables:**
   ```bash
   cd infrastructure
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your values
   ```

3. **Deploy infrastructure:**
   ```bash
   terraform init
   terraform plan
   terraform apply
   ```

4. **Save outputs:**
   ```bash
   terraform output ec2_public_ip  # Save this for GitHub Secrets
   terraform output -raw ec2_private_key > ~/ec2-key.pem
   chmod 400 ~/ec2-key.pem
   ```

### Step 2: Verify EC2 Setup

SSH into your EC2 instance:
```bash
ssh -i ~/ec2-key.pem ubuntu@<EC2_PUBLIC_IP>
```

Verify Docker is installed (Terraform user_data already installed it):
```bash
docker --version
docker compose version
```

Create app directory:
```bash
mkdir -p ~/app
exit
```

### Step 3: Configure GitHub Secrets

Go to your repository → Settings → Secrets and variables → Actions

Add these secrets:

| Secret Name | Description | Example |
|------------|-------------|---------|
| `EC2_IP` | EC2 public IP from Terraform | `54.123.45.67` |
| `EC2_USER` | SSH username | `ubuntu` |
| `SSH_PRIVATE_KEY` | Content of ec2-key.pem | `-----BEGIN RSA PRIVATE KEY-----...` |
| `DOCKER_USERNAME` | Docker Hub username | `johndoe` |
| `DOCKER_PASSWORD` | Docker Hub access token | `dckr_pat_abc123...` |

**To get SSH_PRIVATE_KEY:**
```bash
cat ~/ec2-key.pem
# Copy entire output including BEGIN and END lines
```

**To create Docker Hub token:**
1. Go to https://hub.docker.com/settings/security
2. New Access Token → Read, Write, Delete permissions
3. Copy token and add as `DOCKER_PASSWORD`

### Step 4: Deploy

Push to main branch to trigger deployment:
```bash
git add .
git commit -m "Deploy to production"
git push origin main
```

Or manually trigger from GitHub:
- Go to Actions tab
- Select "Deploy to EC2"
- Click "Run workflow"

### Step 5: Verify Deployment

The workflow will:
1. Build Docker images on GitHub runners
2. Push images to Docker Hub
3. SSH to EC2 and pull images
4. Deploy with docker compose
5. Run health checks

Access your application:
- **Frontend**: http://YOUR_EC2_IP
- **Backend API**: http://YOUR_EC2_IP:8000
- **API Docs**: http://YOUR_EC2_IP:8000/docs
- **Qdrant Dashboard**: http://YOUR_EC2_IP:6333/dashboard

## CI/CD Pipeline

The GitHub Actions workflow automatically:
- Builds optimized Docker images with layer caching
- Pushes to Docker Hub registry
- Deploys to EC2 via SSH
- Runs health checks
- Shows deployment status

**Workflow triggers:**
- Push to `main` branch
- Manual trigger via GitHub Actions UI

## Infrastructure Details

**Terraform provisions:**
- EC2 instance (t3.medium recommended)
- Security groups (ports 22, 80, 8000, 6333)
- Elastic IP for static public IP
- Key pair for SSH access

**Docker services:**
- `qdrant`: Vector database with persistent storage
- `backend`: FastAPI with ML models
- `frontend`: Streamlit UI

## Monitoring and Maintenance

**View logs:**
```bash
ssh -i ~/ec2-key.pem ubuntu@<EC2_IP>
cd ~/app
docker compose logs -f
```

**Restart services:**
```bash
docker compose restart
```

**Update deployment:**
```bash
# Just push to main branch
git push origin main
```

**Rollback:**
```bash
# On EC2
docker compose down
docker compose pull <previous-tag>
docker compose up -d
```

## Troubleshooting

**Backend timeout errors:**
- First request after startup takes 30-60s (model loading)
- Consider using GPU instance (g4dn.xlarge) for faster inference
- Or use external LLM API (OpenAI, Anthropic)

**Deployment fails:**
```bash
# Check GitHub Actions logs
# SSH to EC2 and check:
docker compose ps
docker compose logs backend
```

**Out of disk space:**
```bash
docker system prune -a
```
## License

MIT

## Contributing

Pull requests welcome!
