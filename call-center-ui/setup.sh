#!/bin/bash

# Exit on error
set -e

# Update and install required packages
sudo apt update
sudo apt install -y curl gnupg2 ca-certificates git nginx

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Optional: Install Angular CLI globally (if you want to run ng commands)
# sudo npm install -g @angular/cli

# Clone your Angular app (replace with your repo)
cd ~
git clone https://github.com/your-username/your-angular-repo.git
cd your-angular-repo

# Set env variable to fix OpenSSL issue in Node 18
export NODE_OPTIONS=--openssl-legacy-provider

# Install dependencies
npm install

# Build Angular app for production
npm run build --prod

# Copy built app to NGINX web root
sudo rm -rf /var/www/html/*
sudo cp -r dist/call-center-ui/* /var/www/html/

# Create nginx.conf with Angular routing support
cat << 'EOF' | sudo tee /etc/nginx/conf.d/default.conf
server {
    listen 80;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files \$uri \$uri/ /index.html;
    }

    location ~* \.(?:ico|css|js|gif|jpe?g|png|woff2?|eot|ttf|svg)$ {
        expires 6M;
        access_log off;
        add_header Cache-Control "public";
    }

    error_page 404 /index.html;
}
EOF

# Restart NGINX to apply changes
sudo systemctl restart nginx

# Allow HTTP through firewall (optional)
sudo ufw allow 'Nginx Full'

echo "✅ Angular app deployed and served with NGINX!"
