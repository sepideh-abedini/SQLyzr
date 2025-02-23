set -eo pipefail

usage() {
  echo "Usage $0 [-d BIRD directory] [-r train size] [-t test size]"
  echo "Extracts the first num_samples entries in input_file and write them to a file with .small.json suffix"
  exit 1
}

while getopts "r:t:d:" opt; do
  case $opt in
    d) BIRD_DIR=$OPTARG;;
    r) TRAIN_SIZE=$OPTARG;;
    t) TEST_SIZE=$OPTARG;;
    *) usage ;;
  esac
done

if [ -z "$BIRD_DIR" ] || [ -z "$TEST_SIZE" ]; then
    usage
fi

cd $BIRD_DIR

if [ -n "$TRAIN_SIZE" ]; then
  sample.sh -i data.train.json -n $TRAIN_SIZE
else
  cp data.train.json data.train.small.json
fi

sample.sh -i data.test.json -n $TEST_SIZE

extract_gold.sh -i data.train.small.json
wc -l data.train.small.gold.txt

extract_gold.sh -i data.test.small.json
wc -l data.test.small.gold.txt

tables=$(jq '.[].db_id' data.test.small.json data.train.small.json | uniq | awk -v ORS=, '{print $1}' | sed 's/,$//' )
echo $tables
jq --argjson ids "[$tables]" '[.[] | select(.db_id | IN($ids[]))]' tables.all.json > tables.small.json
