#!/bin/bash

# Deployment script for Resume Manager on AWS
# Usage: ./deploy.sh [staging|production]

set -e

ENV=${1:-production}
SSH_KEY="~/.ssh/aws_resume_manager.pem"
SERVER_IP="your-server-ip"
SERVER_USER="ubuntu"
PROJECT_DIR="/home/ubuntu/resume-manager"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 Starting deployment to ${ENV}...${NC}"

# Check if environment is valid
if [[ ! "$ENV" =~ ^(staging|production)$ ]]; then
    echo "Error: Invalid environment. Use 'staging' or 'production'."
    exit 1
fi

# Build the project locally
echo -e "${YELLOW}🔨 Building Docker images...${NC}"
docker-compose -f docker-compose.prod.yml build

# Create deployment archive
echo -e "${YELLOW}📦 Creating deployment package...${NC}
rm -rf deploy
mkdir -p deploy

# Copy necessary files to deploy directory
cp -r app/ deploy/
cp -r nginx/ deploy/
cp docker-compose.prod.yml deploy/docker-compose.yml
cp .env.prod deploy/.env
cp init.sql deploy/

# Create deployment archive
cd deploy
tar -czf ../deploy.tar.gz .
cd ..

# Upload to server
echo -e "${YELLOW}📤 Uploading files to server...${NC}
scp -i $SSH_KEY deploy.tar.gz ${SERVER_USER}@${SERVER_IP}:/tmp/

# SSH into server and deploy
ssh -i $SSH_KEY ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
    echo -e "\n${YELLOW}🚀 Starting deployment on server...${NC}
    
    # Create project directory if it doesn't exist
    mkdir -p $PROJECT_DIR
    
    # Extract deployment package
    echo -e "${YELLOW}📦 Extracting files...${NC}"
    sudo tar -xzf /tmp/deploy.tar.gz -C $PROJECT_DIR
    
    # Set proper permissions
    sudo chown -R $USER:$USER $PROJECT_DIR
    sudo chmod -R 755 $PROJECT_DIR
    
    # Stop and remove existing containers
    echo -e "${YELLOW}🛑 Stopping existing containers...${NC}"
    cd $PROJECT_DIR
    docker-compose down || true
    
    # Pull latest images
    echo -e "${YELLOW}⬇️  Pulling latest images...${NC}"
    docker-compose pull
    
    # Start services
    echo -e "${YELLOW}🚀 Starting services...${NC}"
    docker-compose up -d --build
    
    # Run database migrations
    echo -e "${YELLOW}🔄 Running database migrations...${NC}"
    docker-compose exec web alembic upgrade head
    
    # Restart nginx
    echo -e "${YELLOW}🔄 Restarting Nginx...${NC}"
    docker-compose restart nginx
    
    # Clean up
    echo -e "${YELLOW}🧹 Cleaning up...${NC}"
    docker system prune -f
    
    echo -e "\n${GREEN}✅ Deployment completed successfully!${NC}"
    echo -e "\n🌐 Application URL: https://yourdomain.com"
    echo -e "📊 Admin Panel: https://yourdomain.com/admin"
ENDSSH

# Clean up local files
echo -e "${YELLOW}🧹 Cleaning up local files...${NC}"
rm -rf deploy deploy.tar.gz

echo -e "\n${GREEN}✅ Deployment process completed!${NC}"
