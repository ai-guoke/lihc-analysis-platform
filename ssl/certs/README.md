# SSL Certificate Setup Instructions

This directory contains SSL certificates for the LIHC Platform.

## Development Setup

For development, you can generate self-signed certificates:

```bash
# Generate private key
openssl genrsa -out ssl/certs/lihc.key 2048

# Generate certificate signing request
openssl req -new -key ssl/certs/lihc.key -out ssl/certs/lihc.csr

# Generate self-signed certificate (valid for 365 days)
openssl x509 -req -days 365 -in ssl/certs/lihc.csr -signkey ssl/certs/lihc.key -out ssl/certs/lihc.crt
```

## Production Setup

For production, use certificates from a trusted Certificate Authority (CA) like:
- Let's Encrypt (free)
- Cloudflare
- DigiCert
- Other commercial CAs

### Let's Encrypt Example

```bash
# Install certbot
sudo apt-get install certbot

# Generate certificates
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates to this directory
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/certs/lihc.crt
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/certs/lihc.key
```

## Certificate Management

### Automated Renewal (Let's Encrypt)

Add to crontab for automatic renewal:
```bash
0 12 * * * /usr/bin/certbot renew --quiet --post-hook "docker-compose restart nginx"
```

### Certificate Information

Check certificate details:
```bash
openssl x509 -in ssl/certs/lihc.crt -text -noout
```

Check certificate expiration:
```bash
openssl x509 -in ssl/certs/lihc.crt -noout -dates
```

## Security Notes

1. Keep private keys secure and never commit them to version control
2. Use strong key sizes (2048 bits minimum, 4096 bits recommended)
3. Regularly update certificates before expiration
4. Monitor certificate expiration dates
5. Use HTTP Strict Transport Security (HSTS) headers
6. Consider certificate pinning for enhanced security

## File Permissions

Set appropriate permissions:
```bash
chmod 600 ssl/certs/lihc.key
chmod 644 ssl/certs/lihc.crt
chown root:root ssl/certs/*
```