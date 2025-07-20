#!/bin/bash

# NGINX Authentication Setup Script for LIHC Platform
# Creates htpasswd file for monitoring endpoints

set -e

HTPASSWD_FILE=".htpasswd"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "Setting up NGINX authentication for LIHC Platform monitoring..."

# Check if htpasswd utility is available
if ! command -v htpasswd &> /dev/null; then
    echo -e "${YELLOW}htpasswd utility not found. Installing apache2-utils...${NC}"
    
    # Try to install htpasswd utility
    if command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y apache2-utils
    elif command -v yum &> /dev/null; then
        sudo yum install -y httpd-tools
    elif command -v brew &> /dev/null; then
        brew install httpd
    else
        echo "Please install apache2-utils or httpd-tools package manually"
        exit 1
    fi
fi

# Prompt for username and password
read -p "Enter monitoring username (default: admin): " username
username=${username:-admin}

# Generate secure password if not provided
read -s -p "Enter password for $username (leave empty to generate): " password
echo

if [ -z "$password" ]; then
    # Generate a secure random password
    password=$(openssl rand -base64 12)
    echo -e "${YELLOW}Generated password: $password${NC}"
    echo -e "${YELLOW}Please save this password securely!${NC}"
fi

# Create htpasswd file
htpasswd -c -b "$HTPASSWD_FILE" "$username" "$password"

# Set appropriate permissions
chmod 644 "$HTPASSWD_FILE"

echo -e "${GREEN}NGINX authentication file created successfully!${NC}"
echo "File: $HTPASSWD_FILE"
echo "Username: $username"
echo "Use this file in your NGINX configuration for protecting monitoring endpoints."

# Display usage instructions
cat << EOF

To use this authentication file in NGINX:

1. Copy the file to your NGINX configuration directory:
   sudo cp $HTPASSWD_FILE /etc/nginx/

2. Update your NGINX configuration:
   location /monitoring/ {
       auth_basic "Monitoring Access";
       auth_basic_user_file /etc/nginx/.htpasswd;
       # ... rest of your location config
   }

3. Reload NGINX:
   sudo nginx -s reload

EOF