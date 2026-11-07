# Frontend image: Nginx serves static files and proxies API requests
FROM nginx:1.27-alpine

# Replace default Nginx config with our own
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy static website
COPY html/ /usr/share/nginx/html/

EXPOSE 80
