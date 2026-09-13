# ==============================================================================
# NirmaanAI Frontend Dashboard Dockerfile (Phase 24)
# Multi-Stage Production Build: Node 20 Builder + Nginx Alpine Runner
# ==============================================================================

# ------------------------------------------------------------------------------
# Stage 1: Build React 19 / Vite Application
# ------------------------------------------------------------------------------
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package manifests for dependency layer caching
COPY package.json ./

RUN npm install

# Copy source code and assets
COPY . .

# Compile optimized production bundle into /app/dist
RUN npm run build

# ------------------------------------------------------------------------------
# Stage 2: Serve Production Assets with Nginx Alpine
# ------------------------------------------------------------------------------
FROM nginx:1.27-alpine AS runner

LABEL maintainer="NirmaanAI Core Platform Team <engineering@nirmaanai.internal>" \
      version="0.24.0" \
      description="Production Nginx container serving NirmaanAI React Dashboard"

# Copy pre-compiled distribution assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy customized Nginx server configuration with reverse proxy
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

# Healthcheck probing Nginx /healthz endpoint
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget -q -O - http://127.0.0.1/healthz | grep -q "healthy" || exit 1

CMD ["nginx", "-g", "daemon off;"]
