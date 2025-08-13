#!/bin/bash

# ===================================
# GitHub Repository Upload Script
# ===================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== LIHC Platform GitHub Upload ===${NC}"
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo -e "${YELLOW}Initializing git repository...${NC}"
    git init
    echo -e "${GREEN}✓ Git repository initialized${NC}"
else
    echo -e "${GREEN}✓ Git repository already initialized${NC}"
fi

# Check current branch
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "main")
if [ -z "$CURRENT_BRANCH" ]; then
    git checkout -b main
    CURRENT_BRANCH="main"
fi
echo -e "${BLUE}Current branch: $CURRENT_BRANCH${NC}"

# Add all files
echo -e "${YELLOW}Adding files to git...${NC}"
git add -A
echo -e "${GREEN}✓ Files added${NC}"

# Commit changes
echo -e "${YELLOW}Creating commit...${NC}"
COMMIT_MSG="feat: 🚀 LIHC Platform v2.6 - Complete project with CI/CD

- Added comprehensive documentation (README, DEPLOYMENT, QUICKSTART, DEVELOPMENT)
- Configured Docker and docker-compose for containerization
- Added Makefile for common operations
- Implemented GitHub Actions CI/CD pipeline
- Added Apple glassmorphism UI design
- Configured environment templates and examples
- Added security scanning and dependency management"

git commit -m "$COMMIT_MSG" || echo -e "${YELLOW}No changes to commit or already committed${NC}"

# Check if remote exists
if git remote | grep -q "origin"; then
    echo -e "${YELLOW}Remote 'origin' already exists${NC}"
    REMOTE_URL=$(git remote get-url origin)
    echo -e "${BLUE}Current remote: $REMOTE_URL${NC}"
    
    read -p "Do you want to use this remote? (y/n): " use_existing
    if [ "$use_existing" != "y" ]; then
        git remote remove origin
        read -p "Enter new GitHub repository URL (e.g., https://github.com/username/repo.git): " REPO_URL
        git remote add origin "$REPO_URL"
    fi
else
    echo -e "${YELLOW}No remote repository configured${NC}"
    echo "Please enter your GitHub repository URL"
    echo "Format: https://github.com/username/repository-name.git"
    read -p "Repository URL: " REPO_URL
    
    if [ ! -z "$REPO_URL" ]; then
        git remote add origin "$REPO_URL"
        echo -e "${GREEN}✓ Remote repository added${NC}"
    else
        echo -e "${RED}No repository URL provided. Exiting.${NC}"
        exit 1
    fi
fi

# Create .gitignore if it doesn't exist
if [ ! -f .gitignore ]; then
    echo -e "${YELLOW}Creating .gitignore...${NC}"
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
*.egg-info/
dist/
build/

# Environment
.env
.env.local
.env.*.local
!.env.example

# IDE
.vscode/
.idea/
*.swp
*.swo
.DS_Store

# Testing
.coverage
htmlcov/
.pytest_cache/
.tox/

# Logs
*.log
logs/
!logs/.gitkeep

# Data
data/user/*
!data/user/.gitkeep
data/processed/*
!data/processed/.gitkeep

# Results
results/user_analyses/*
!results/user_analyses/.gitkeep

# Temporary
tmp/
temp/
*.tmp

# Backups
backups/*
!backups/.gitkeep
*.backup
*.bak

# Docker
.dockerignore
docker-compose.override.yml

# Secrets
*.pem
*.key
*.crt
secrets/
EOF
    git add .gitignore
    git commit -m "chore: Add comprehensive .gitignore" || true
    echo -e "${GREEN}✓ .gitignore created${NC}"
fi

# Push to GitHub
echo ""
echo -e "${YELLOW}Ready to push to GitHub!${NC}"
echo -e "${BLUE}This will push to branch: $CURRENT_BRANCH${NC}"
read -p "Continue with push? (y/n): " confirm

if [ "$confirm" == "y" ]; then
    echo -e "${YELLOW}Pushing to GitHub...${NC}"
    
    # Try to push, handling different scenarios
    if git push -u origin "$CURRENT_BRANCH" 2>/dev/null; then
        echo -e "${GREEN}✓ Successfully pushed to GitHub!${NC}"
    else
        echo -e "${YELLOW}Push failed. Trying with force...${NC}"
        read -p "Force push? This will overwrite remote changes (y/n): " force
        if [ "$force" == "y" ]; then
            git push -u origin "$CURRENT_BRANCH" --force
            echo -e "${GREEN}✓ Force pushed to GitHub!${NC}"
        else
            echo -e "${RED}Push cancelled.${NC}"
            echo "You may need to:"
            echo "1. Pull remote changes: git pull origin $CURRENT_BRANCH"
            echo "2. Resolve conflicts if any"
            echo "3. Push again: git push origin $CURRENT_BRANCH"
            exit 1
        fi
    fi
    
    # Create and push tags
    echo ""
    read -p "Do you want to create a version tag (v2.6.0)? (y/n): " create_tag
    if [ "$create_tag" == "y" ]; then
        git tag -a v2.6.0 -m "Release version 2.6.0 - Complete platform with CI/CD"
        git push origin v2.6.0
        echo -e "${GREEN}✓ Version tag v2.6.0 created and pushed${NC}"
    fi
    
    # Get repository URL for display
    REPO_URL=$(git remote get-url origin)
    REPO_URL_DISPLAY=${REPO_URL%.git}
    
    # Convert SSH to HTTPS for display
    if [[ $REPO_URL_DISPLAY == git@github.com:* ]]; then
        REPO_URL_DISPLAY=${REPO_URL_DISPLAY/git@github.com:/https://github.com/}
    fi
    
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ Upload Complete!${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════${NC}"
    echo ""
    echo -e "${BLUE}Repository URL:${NC} $REPO_URL_DISPLAY"
    echo -e "${BLUE}Actions URL:${NC} $REPO_URL_DISPLAY/actions"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "1. Visit your repository: $REPO_URL_DISPLAY"
    echo "2. Check GitHub Actions: $REPO_URL_DISPLAY/actions"
    echo "3. Configure Secrets: $REPO_URL_DISPLAY/settings/secrets/actions"
    echo "4. Set up Environments: $REPO_URL_DISPLAY/settings/environments"
    echo ""
    echo -e "${BLUE}Quick Setup Commands:${NC}"
    echo "  ./scripts/setup-github-secrets.sh  # Configure secrets"
    echo "  make info                          # Check project info"
    echo "  make help                          # See all commands"
    echo ""
else
    echo -e "${YELLOW}Push cancelled. Your changes are committed locally.${NC}"
    echo "To push later, run: git push -u origin $CURRENT_BRANCH"
fi