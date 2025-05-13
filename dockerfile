# Base image from Ollama's official image
FROM ghcr.io/ollama/ollama:latest

# Expose the default port
EXPOSE 11443

# Download the desired model during image build
RUN ollama pull phi3:medium

# Run Ollama when the container starts
ENTRYPOINT ["ollama", "serve", "--port", "11443"]