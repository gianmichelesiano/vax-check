FROM node:20-alpine AS builder
WORKDIR /app
ENV NEXT_PUBLIC_API_PROXY="http://api:8000/api/:path*"
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine
WORKDIR /app
ENV NEXT_PUBLIC_API_URL=""
ENV NEXT_PUBLIC_API_PROXY="http://api:8000/api/:path*"
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/next.config.mjs ./
EXPOSE 3000
CMD ["npx", "next", "start", "-p", "3000"]
