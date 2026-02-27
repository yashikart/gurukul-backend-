# Build stage - run with context at repo root so prana-core is available
FROM node:20-alpine AS build
# prana-core is imported by gurukul_prana.js and src/utils as ../prana-core (from Frontend = repo root)
COPY prana-core /prana-core
COPY Frontend /app
WORKDIR /app
RUN npm ci
ARG VITE_API_URL=http://localhost:3000
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

# Serve stage
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
RUN echo 'server { listen 80; root /usr/share/nginx/html; index index.html; location / { try_files $uri $uri/ /index.html; } }' > /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
