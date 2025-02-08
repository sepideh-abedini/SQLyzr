docker build . -t sqlyzr
docker run --rm -it --env-file .env \
  -v "./data:/app/data" \
  -v "./conf.json:/app/conf.json" \
  sqlyzr