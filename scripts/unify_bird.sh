set -eo pipefail

BIRD_DIR=$1

SCRIPT_DIR=$(dirname "$(realpath "$0")")

cd $BIRD_DIR

mkdir -p database

if [ ! -d "dev/dev_databases" ]; then
  mv "dev/dev_databases/"*/ "database/"
fi

#if [ ! -d "train/train_databases" ]; then
#  mv "train/train_databases/"*/ "database/"
#fi


concat.sh -o "tables.json" "dev/dev_tables.json" "train/train_tables.json"

rename_field.sh -i "dev/dev.json" -f "SQL" -n "query"
rename_field.sh -i "train/train.json" -f "SQL" -n "query"
#
sample.sh -i "dev/dev.json" -n 10
mv "dev/dev.small.json" small.json

cp "dev/dev.json" dev.json
cp "train/train.json" train.json

concat.sh -o all.json dev.json train.json

for size in "small"; do
    mkdir -p "$size"
    cp "$size.json" $size/data.json
    cp tables.json "$size/tables.json"
    python3 "$SCRIPT_DIR/clean.py" -f "$(realpath $size/data.json)" -d "$(realpath database)"
    extract_gold.sh -i "$size/data.json"
done
