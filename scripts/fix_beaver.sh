set -eo pipefail

usage() {
  echo "Usage $0 [-d Beaver directory]"
  exit 1
}

while getopts "d:" opt; do
  case $opt in
    d) BEAVER_DIR=$OPTARG;;
    *) usage ;;
  esac
done

if [ -z "$BEAVER_DIR" ] ; then
    usage
fi

PARENT_DIR="$(dirname "$(realpath "$0")")"

cd "$BEAVER_DIR"

python3.11 $PARENT_DIR/fix_beaver_table.py -i dev_tables.json -o tables.json

concat.sh -o data.all.json dev_dw.json dev_nw.json

cp data.all.json data.train.json
cp data.all.json data.test.json

echo "Num train $(jq '. | length' data.train.json)"
echo "Num test $(jq '. | length' data.test.json)"

echo "Num dbs $(jq '. | length' tables.json)"

for size in "train" "test"; do
    FILE_NAME="data.$size.json"
    rename_field.sh -i $FILE_NAME -f "sql" -n "query"
    extract_gold.sh -i $FILE_NAME
    jq "length" "data.$size.json"
    wc -l "data.$size.gold.txt"
done
