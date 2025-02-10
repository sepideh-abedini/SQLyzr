#### Login to Github Container Registry

- Go to [Github Access Tokens](https://github.com/settings/tokens) settings
- Grant `read:package`, `write:package`, and `delete:package` accesses to the token
- Login into ghcr.io using your username and token as the password:

```shell
docker login ghcr.io -u $GH_USERNAME
```

#### Pull Image

```shell
docker pull $IMAGE_TAG
```

#### Create config and env files
You need to create the `conf.json` and `.env` files.

`conf.json`: Contains the SQLyzr configurations
`.env`: Contains the API tokens and some other runtime configs

#### Run a SQLyzr container

```shell
docker run --rm -it --env-file .env \
-v ./conf.json:/app/conf.json \
-v ./data:/app/data \
$IMAGE_TAG
```

#### Run SQLyzr

After starting the container, you get shell access to it.
Here is an example of how to download a dataset and run
SQLyzr on it:
##### Spider Example
- First, download the [Spider dataset](https://yale-lily.github.io/spider) and extract it
to the `data/spider` directory (do it on host machine).
- Validate and fix the spider dataset:
```shell
unify_spider.sh data/spider
```
- Run sqlyzr
- 
```shell
sqlyzr
```
