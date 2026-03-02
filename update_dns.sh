#!/bin/bash

ENV_FILE="/home/ubuntu/InvestApp/.env"
if [[ ! -f "$ENV_FILE" ]]; then
    echo "Error: .env file not found at $ENV_FILE"
    exit 1
fi
source "$ENV_FILE"

# 1. Get the current public IP address of the server
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
NEW_IP=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/public-ipv4)

if [[ -z "$NEW_IP" ]]; then
    echo "Error: Could not find an IP."
    exit 1
fi

# 2. Send a request to Cloudflare API to update the DNS record
curl -s -X PUT "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records/$RECORD_ID" \
     -H "Authorization: Bearer $API_TOKEN" \
     -H "Content-Type: application/json" \
     --data '{"type":"A","name":"'"$DOMAIN"'","content":"'"$NEW_IP"'","ttl":60,"proxied":false}'

echo "DNS record for $DOMAIN updated to $NEW_IP"