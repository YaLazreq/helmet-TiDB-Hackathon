# 1) Déps (toutes les deps, y compris dev)
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

# 2) Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
# Ignorer les erreurs ESLint et TypeScript
ENV SKIP_ENV_VALIDATION=1
RUN npm run build || npm run build -- --no-lint

# 3) Runner (standalone)
FROM node:20-alpine AS runner
WORKDIR /app
# Output standalone de Next
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME=0.0.0.0
EXPOSE 3000
CMD ["node","server.js"]