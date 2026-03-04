# Build stage
FROM node:16-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Use npm install instead of npm ci to ignore lockfile errors
RUN npm install

# Copy the rest of the source code
COPY . .

# Set CI environment variable to false to treat warnings as non-fatal (mirrors pipeline)
ENV CI=false
RUN npm run build

# Production stage
FROM nginx:alpine

COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]