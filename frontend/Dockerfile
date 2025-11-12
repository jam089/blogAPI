FROM node:22-alpine AS build
WORKDIR /app
COPY ./frontend/package*.json ./
RUN npm install --legacy-peer-deps
COPY ./frontend/ .
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]