#!/bin/bash
sudo docker login ghcr.io --username danielpicone -p $CR_PAT
echo "Pulling latest image from ghcr.io/danielpicone/bloodontheclocktowerpython:latest"
sudo docker pull ghcr.io/danielpicone/bloodontheclocktowerpython:latest
echo "Creating and running container in the background"
sudo docker run --env-file .env -d --restart=unless-stopped ghcr.io/danielpicone/bloodontheclocktowerpython:latest
