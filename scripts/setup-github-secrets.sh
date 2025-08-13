#!/bin/bash

# ===================================
# GitHub Secrets Setup Script
# ===================================
# This script helps you set up GitHub secrets for CI/CD
# Usage: ./scripts/setup-github-secrets.sh

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}GitHub Secrets Setup for LIHC Platform${NC}"
echo "========================================"
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}GitHub CLI (gh) is not installed!${NC}"
    echo "Please install it first: https://cli.github.com/"
    exit 1
fi

# Check if logged in to GitHub
if ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}Not logged in to GitHub. Logging in...${NC}"
    gh auth login
fi

# Get repository name
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
echo -e "${GREEN}Setting up secrets for repository: $REPO${NC}"
echo ""

# Function to set secret
set_secret() {
    local name=$1
    local description=$2
    local required=$3
    
    echo -e "${YELLOW}$name${NC} - $description"
    
    if [ "$required" == "true" ]; then
        echo -e "${RED}(Required)${NC}"
    else
        echo -e "${BLUE}(Optional)${NC}"
    fi
    
    read -p "Enter value (or press Enter to skip): " value
    
    if [ ! -z "$value" ]; then
        echo "$value" | gh secret set "$name"
        echo -e "${GREEN}✓ $name set successfully${NC}"
    else
        if [ "$required" == "true" ]; then
            echo -e "${RED}⚠ Warning: $name is required for CI/CD to work properly${NC}"
        else
            echo -e "${BLUE}Skipped $name${NC}"
        fi
    fi
    echo ""
}

# Function to set secret from file
set_secret_from_file() {
    local name=$1
    local description=$2
    local required=$3
    
    echo -e "${YELLOW}$name${NC} - $description"
    
    if [ "$required" == "true" ]; then
        echo -e "${RED}(Required)${NC}"
    else
        echo -e "${BLUE}(Optional)${NC}"
    fi
    
    read -p "Enter file path (or press Enter to skip): " filepath
    
    if [ ! -z "$filepath" ] && [ -f "$filepath" ]; then
        gh secret set "$name" < "$filepath"
        echo -e "${GREEN}✓ $name set successfully from file${NC}"
    else
        if [ "$required" == "true" ]; then
            echo -e "${RED}⚠ Warning: $name is required for CI/CD to work properly${NC}"
        else
            echo -e "${BLUE}Skipped $name${NC}"
        fi
    fi
    echo ""
}

echo "=== Deployment Secrets ==="
echo ""

# Staging deployment
echo "--- Staging Environment ---"
set_secret "STAGING_HOST" "Staging server hostname or IP" "false"
set_secret "STAGING_USER" "Staging server SSH username" "false"
set_secret_from_file "STAGING_SSH_KEY" "Staging server SSH private key (file path)" "false"

# Production deployment
echo "--- Production Environment ---"
set_secret "PROD_HOST" "Production server hostname or IP" "false"
set_secret "PROD_USER" "Production server SSH username" "false"
set_secret_from_file "PROD_SSH_KEY" "Production server SSH private key (file path)" "false"

# Kubernetes (if using)
echo "--- Kubernetes (Optional) ---"
read -p "Are you using Kubernetes? (y/n): " use_k8s
if [ "$use_k8s" == "y" ]; then
    echo "Encode your kubeconfig file with: base64 < ~/.kube/config"
    set_secret "KUBE_CONFIG" "Base64 encoded Kubernetes config" "false"
fi

echo ""
echo "=== Notification Secrets ==="
echo ""

set_secret "SLACK_WEBHOOK" "Slack webhook URL for notifications" "false"

echo ""
echo "=== Monitoring Secrets ==="
echo ""

set_secret "DATADOG_API_KEY" "DataDog API key for monitoring" "false"
set_secret "DATADOG_PUBLIC_ID" "DataDog synthetic test public ID" "false"

echo ""
echo "=== Security Scanning ==="
echo ""

set_secret "SNYK_TOKEN" "Snyk authentication token" "false"

echo ""
echo "=== Database Credentials ==="
echo ""

set_secret "DB_PASSWORD" "Production database password" "false"
set_secret "REDIS_PASSWORD" "Redis password (if using authentication)" "false"

echo ""
echo -e "${GREEN}✅ Secret setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Create environments in GitHub Settings → Environments"
echo "   - staging (auto-deploy from develop branch)"
echo "   - production (requires approval, deploy from main branch)"
echo ""
echo "2. Configure branch protection rules:"
echo "   - main: Require PR reviews, status checks"
echo "   - develop: Require status checks"
echo ""
echo "3. Enable GitHub Pages for documentation (optional):"
echo "   - Settings → Pages → Source: gh-pages branch"
echo ""
echo "4. Configure Dependabot security updates:"
echo "   - Settings → Security → Dependabot alerts"
echo ""

# Create a summary file
cat > github-secrets-summary.txt << EOF
GitHub Secrets Configuration Summary
====================================
Repository: $REPO
Date: $(date)

Configured Secrets:
------------------
$(gh secret list)

Environments to Create:
----------------------
1. staging
   - URL: https://staging.your-domain.com
   - Auto-deploy from: develop branch
   
2. production
   - URL: https://your-domain.com
   - Requires approval: Yes
   - Deploy from: main branch

Branch Protection Rules:
-----------------------
1. main branch:
   - Require pull request reviews
   - Require status checks to pass
   - Include administrators
   
2. develop branch:
   - Require status checks to pass

Additional Setup:
----------------
- Enable GitHub Pages (optional)
- Configure Dependabot alerts
- Set up team access permissions
EOF

echo -e "${BLUE}Configuration summary saved to: github-secrets-summary.txt${NC}"
echo ""
echo -e "${GREEN}🎉 Setup complete! Your CI/CD pipeline is ready to use.${NC}"