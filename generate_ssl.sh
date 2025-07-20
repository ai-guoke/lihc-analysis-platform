#!/bin/bash

# SSL Certificate Generation Script for LIHC Platform
# This script generates self-signed certificates for development use

set -e

CERT_DIR="ssl/certs"
KEY_FILE="$CERT_DIR/lihc.key"
CERT_FILE="$CERT_DIR/lihc.crt"
CSR_FILE="$CERT_DIR/lihc.csr"

echo "Generating SSL certificates for LIHC Platform..."

# Create certificate directory if it doesn't exist
mkdir -p "$CERT_DIR"

# Generate private key
echo "Generating private key..."
openssl genrsa -out "$KEY_FILE" 2048

# Generate certificate signing request
echo "Generating certificate signing request..."
openssl req -new -key "$KEY_FILE" -out "$CSR_FILE" -subj "/C=US/ST=State/L=City/O=LIHC Platform/OU=Development/CN=localhost"

# Generate self-signed certificate
echo "Generating self-signed certificate..."
openssl x509 -req -days 365 -in "$CSR_FILE" -signkey "$KEY_FILE" -out "$CERT_FILE"

# Set appropriate permissions
chmod 600 "$KEY_FILE"
chmod 644 "$CERT_FILE"

# Clean up CSR file
rm "$CSR_FILE"

echo "SSL certificates generated successfully:"
echo "  Private key: $KEY_FILE"
echo "  Certificate: $CERT_FILE"
echo ""
echo "Certificate details:"
openssl x509 -in "$CERT_FILE" -text -noout | grep -A 2 "Subject:"
openssl x509 -in "$CERT_FILE" -text -noout | grep -A 2 "Validity"

echo ""
echo "Note: These are self-signed certificates for development use only."
echo "For production, please use certificates from a trusted CA."