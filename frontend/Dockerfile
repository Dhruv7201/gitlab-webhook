# Stage 1: Build the TypeScript application
FROM node:18.19.0 AS build-step

# Use an argument for the API URL
ARG API_URL

# Set the working directory
WORKDIR /build

# Copy package.json and package-lock.json
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application files
COPY . .

# Set environment variable for the API URL
ENV REACT_APP_API_URL=${API_URL}

# Echo the API URL for debugging purposes
RUN echo ${API_URL}

# Build the application
RUN npm run build

# Stage 2: Serve the application using Nginx
FROM nginx:1.18-alpine

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy the built application from the previous stage
COPY --from=build-step /build/dist /react-app/build
