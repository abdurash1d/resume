# AWS Deployment Guide for Resume Manager

This guide will walk you through deploying the Resume Manager application to an AWS EC2 instance.

## Prerequisites

1. AWS Account with appropriate permissions
2. AWS CLI installed and configured
3. Docker and Docker Compose installed locally
4. SSH key pair for EC2 instance access
5. Domain name (optional, but recommended for production)

## Step 1: Set Up EC2 Instance

1. Launch a new EC2 instance:
   - **AMI**: Ubuntu Server 22.04 LTS (HVM), SSD Volume Type
   - **Instance Type**: t3.small (or larger for production)
   - **Storage**: 30GB GP2 (SSD)
   - **Security Group**:
     - SSH (port 22) - Your IP only
     - HTTP (port 80) - 0.0.0.0/0
     - HTTPS (port 443) - 0.0.0.0/0
     - Custom TCP (ports 8000-8010) - For application

2. Connect to your instance:
   ```bash
   chmod 400 your-key.pem
   ssh -i your-key.pem ubuntu@your-instance-ip
   ```

## Step 2: Install Dependencies on EC2

```bash
# Update packages
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add current user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

## Step 3: Configure Environment Variables

1. On your local machine, create a `.env.prod` file based on `.env.example`
2. Update the following variables for production:
   ```env
   DEBUG=False
   SECRET_KEY=your-secure-secret-key
   DATABASE_URL=postgresql://postgres:your-secure-password@db:5432/resume_db
   ```

## Step 4: Deploy the Application

1. Copy your deployment files to the server:
   ```bash
   # From your local machine
   scp -i your-key.pem -r . ubuntu@your-instance-ip:~/resume-manager
   ```

2. SSH into your instance and start the services:
   ```bash
   cd ~/resume-manager
   docker-compose -f docker-compose.prod.yml up -d --build
   ```

## Step 5: Set Up SSL with Let's Encrypt (Optional but Recommended)

1. SSH into your instance and run:
   ```bash
   # Install Certbot
   sudo apt-get install -y certbot python3-certbot-nginx
   
   # Stop Nginx container temporarily
   docker-compose -f docker-compose.prod.yml stop nginx
   
   # Get SSL certificate
   sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com
   
   # Update Nginx configuration with your domain
   # (Edit nginx/nginx.conf and replace 'yourdomain.com' with your actual domain)
   
   # Restart services
   docker-compose -f docker-compose.prod.yml up -d
   
   # Set up automatic renewal
   echo "0 0,12 * * * root /usr/bin/certbot renew --quiet" | sudo tee -a /etc/cron.d/certbot
   ```

## Step 6: Set Up Automatic Updates (Optional)

Create a script to automatically update the application:

```bash
#!/bin/bash
cd /home/ubuntu/resume-manager
git pull
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml exec web alembic upgrade head
```

## Step 7: Monitoring and Maintenance

1. **View logs**:
   ```bash
   docker-compose -f docker-compose.prod.yml logs -f
   ```

2. **Backup database**:
   ```bash
   # Create backup
   docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U postgres resume_db > backup_$(date +%Y-%m-%d).sql
   
   # Restore from backup
   cat backup_file.sql | docker-compose -f docker-compose.prod.yml exec -T db psql -U postgres resume_db
   ```

## Troubleshooting

1. **Port already in use**:
   ```bash
   sudo lsof -i :80  # Find process using port 80
   sudo kill <PID>    # Kill the process
   ```

2. **Docker permission issues**:
   ```bash
   sudo usermod -aG docker $USER
   newgrp docker
   ```

3. **View running containers**:
   ```bash
   docker ps
   docker-compose -f docker-compose.prod.yml ps
   ```

## Security Best Practices

1. **Regularly update your system**:
   ```bash
   sudo apt-get update && sudo apt-get upgrade -y
   ```

2. **Use strong passwords** for all services
3. **Enable automatic security updates**:
   ```bash
   sudo apt-get install -y unattended-upgrades
   sudo dpkg-reconfigure -plow unattended-upgrades
   ```

4. **Set up a firewall** (UFW):
   ```bash
   sudo ufw allow ssh
   sudo ufw allow http
   sudo ufw allow https
   sudo ufw enable
   ```

## Scaling

For production with higher traffic, consider:
1. Using a larger EC2 instance type
2. Setting up a load balancer
3. Using RDS for the database
4. Implementing Redis for caching
5. Setting up auto-scaling groups

## Backup Strategy

1. **Database Backups**:
   - Set up daily database dumps
   - Store backups in S3 with versioning enabled
   - Test restoration process regularly

2. **Application Backups**:
   - Use EBS snapshots for the entire instance
   - Keep multiple backup versions
   - Store backups in a different AWS region

## Monitoring

1. **AWS CloudWatch**:
   - Set up basic monitoring
   - Create alarms for high CPU, memory usage
   - Monitor disk space

2. **Application Logs**:
   - Forward logs to CloudWatch Logs
   - Set up log rotation
   - Monitor for errors and exceptions

## Cost Optimization

1. **Reserved Instances**: Consider reserved instances for long-term cost savings
2. **Spot Instances**: Use spot instances for non-critical workloads
3. **Clean up unused resources**
4. **Monitor costs** with AWS Cost Explorer

## Maintenance

1. **Regularly update dependencies**:
   ```bash
   docker-compose -f docker-compose.prod.yml build --no-cache
   docker-compose -f docker-compose.prod.yml up -d
   ```

2. **Monitor disk space**:
   ```bash
   df -h
   docker system df
   ```

3. **Clean up old containers and images**:
   ```bash
   docker system prune -a --volumes
   ```

## Support

For support, please open an issue in the GitHub repository or contact the development team.

---

**Note**: This is a basic deployment guide. For production environments, consider implementing additional security measures and consulting with a DevOps professional.
