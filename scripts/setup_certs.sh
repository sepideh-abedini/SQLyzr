
certbot certonly  --manual  --preferred-challenges dns  -d "*.$SQLYZR_DOMAIN" -d "$SQLYZR_DOMAIN"
mkdir -p /certs
cp -L /etc/letsencrypt/live/sqlyzr.site/* /certs