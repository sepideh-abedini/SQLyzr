#### Login to Github Container Registry
- Go to [Github Access Tokens](https://github.com/settings/tokens) settings
- Grant `read:package`, `write:package`, and `delete:package` accesses to the token
- Login into ghcr.io using your username and token as the password:
```shell
docker login ghcr.io -u $GH_USERNAME
```
#### Pull Image
```shell
docker pull docker pull $IMAGE_TAG
```
