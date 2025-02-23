set -eo pipefail

usage() {
  echo "Usage $0 [-d SPIDER directory]"
  exit 1
}

while getopts "zd:" opt; do
  case $opt in
    z) UNARCHIVE=1;;
    d) BIRD_DIR=$OPTARG;;
    *) usage ;;
  esac
done

unzip -n spider_data.zip

SPIDER_DIR=spider_data

cd $SPIDER_DIR

cp -r test_database/* database

concat.sh -o tables.all.json tables.json test_tables.json

echo "Num tables $(jq '. | length' tables.all.json)"

cp dev.json data.train.json
echo "Num train $(jq '. | length' data.train.json)"

concat.sh -o data.test.json train_spider.json test.json
echo "Num test $(jq '. | length' data.test.json)"

for size in "train" "test" "train.small" "test.small"; do
    extract_gold.sh -i "data.$size.json"
    wc -l "data.$size.gold.txt"
done
