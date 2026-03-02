#!/bin/bash


source "$(dirname "$0")/.env"

# 1. Get the current public IP address of the server

NEW_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)

# 2. Send a request to Cloudflare API to update the DNS record
curl -s -X PUT "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records/$RECORD_ID" \
     -H "Authorization: Bearer $API_TOKEN" \
     -H "Content-Type: application/json" \
     --data '{"type":"A","name":"'"$DOMAIN"'","content":"'"$NEW_IP"'","ttl":60,"proxied":false}'

echo "DNS record for $DOMAIN updated to $NEW_IP"