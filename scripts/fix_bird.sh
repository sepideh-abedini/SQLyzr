set -eo pipefail

usage() {
  echo "Usage $0 [-d BIRD directory] [-z]"
  exit 1
}

while getopts "zd:" opt; do
  case $opt in
    z) UNARCHIVE=1;;
    d) BIRD_DIR=$OPTARG;;
    *) usage ;;
  esac
done

if [ -z "$BIRD_DIR" ] ; then
    usage
fi

cd $BIRD_DIR

if [ -n "$UNARCHIVE" ]; then
  rm -rf database
  mkdir -p database

  rm -rf dev
  unzip -n dev.zip
  mv dev_20240627 dev
  unzip -n dev/dev_databases.zip -d dev

  unzip -n train.zip
  unzip -n train/train_databases.zip -d train

  mv -v "dev/dev_databases/"* "database/"
  mv -v "train/train_databases/"* "database/"
fi

concat.sh -o tables.all.json train/train_tables.json dev/dev_tables.json

echo "Num tables $(jq '. | length' tables.all.json)"

cp dev/dev.json data.train.json
echo "Num train $(jq '. | length' data.train.json)"

cp train/train.json data.test.json
echo "Num test $(jq '. | length' data.test.json)"

for size in "train" "test"; do
    FILE_NAME="data.$size.json"
    rename_field.sh -i $FILE_NAME -f "SQL" -n "query"
    jq '[.[] | select(.query | startswith("WITH") | not)]' $FILE_NAME > "$FILE_NAME".clean
    mv $FILE_NAME.clean $FILE_NAME
    extract_gold.sh -i $FILE_NAME
    jq "length" "data.$size.json"
    wc -l "data.$size.gold.txt"
done
