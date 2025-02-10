set -eo pipefail

SPIDER_DIR=$1

SCRIPT_DIR=$(dirname "$(realpath "$0")")

cd $SPIDER_DIR

cp -r "test_database/"* "database"

concat.sh -o tables.all.json tables.json test_tables.json

sample.sh -i dev.json -n 10
mv dev.small.json small.json

cp train_spider.json train.json

concat.sh -o all.json dev.json test.json train.json

for size in "small" "dev" "test" "train" "all"; do
    mkdir -p "$size"
    cp "$size.json" $size/data.json
    cp tables.all.json "$size/tables.json"
    python3 "$SCRIPT_DIR/clean.py" -f "$(realpath $size/data.json)" -d "$(realpath database)"
    extract_gold.sh -i "$size/data.json"
done
