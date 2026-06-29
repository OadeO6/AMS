# Multi-stage production build for React/Vite using pnpm and Nginx
# ---------------------------------------------------------------------------
# Stage 1: Build
# ---------------------------------------------------------------------------
FROM node:20-alpine AS builder

# Enable pnpm
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

WORKDIR /app

# Copy lockfile and package.json first to cache dependencies
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy the rest of the application
COPY . .

# Set build arguments for Vite env variables
ARG VITE_API_URL=http://localhost:8000
ARG VITE_TRPC_URL=http://localhost:8000/api/trpc

ENV VITE_API_URL=$VITE_API_URL
ENV VITE_TRPC_URL=$VITE_TRPC_URL

# Build the frontend
RUN pnpm build

# ---------------------------------------------------------------------------
# Stage 2: Serve using Nginx
# ---------------------------------------------------------------------------
FROM nginx:alpine AS runtime

# Copy custom nginx configuration to support React routing
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy the built files to the nginx html directory
COPY --from=builder /app/dist/public /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
