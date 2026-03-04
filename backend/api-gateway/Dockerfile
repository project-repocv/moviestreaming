# api-gateway/Dockerfile
FROM eclipse-temurin:11-jre-alpine

# Create a non-root user
RUN addgroup -S cinevision && adduser -S cinevision -G cinevision -u 1000
USER cinevision

WORKDIR /app

# Copy the jar file
COPY target/*.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]