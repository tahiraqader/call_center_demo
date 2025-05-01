# Use Node.js image for building
FROM node:18 AS builder

WORKDIR /app

# Set environment variable to fix OpenSSL issue in Node 18
ENV NODE_OPTIONS=--openssl-legacy-provider

# Copy package files and install dependencies
COPY package.json package-lock.json ./
RUN npm install

# Copy source code
COPY . .

# Build Angular app for production
RUN npm run build --prod

# ---------- Serve Stage ----------
FROM nginx:alpine

# Copy built app from builder stage
COPY --from=builder /app/dist/call-center-ui /usr/share/nginx/html

# Copy custom NGINX config (for Angular routing support)
COPY nginx.conf /etc/nginx/conf.d/default.conf
    