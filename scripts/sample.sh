set -euo pipefail

usage() {
  echo "Usage $0 [-i input_file] [-n num_samples]"
  echo "Extracts the first num_samples entries in input_file and write them to a file with .small.json suffix"
  exit 1
}

while getopts "i:n:" opt; do
  case $opt in
    i) FILE_PATH=$OPTARG;;
    n) NUM_SAMPLES=$OPTARG;;
    *) usage ;;
  esac
done

if [ -z "$FILE_PATH" ] || [ -z "$NUM_SAMPLES" ]; then
    usage
fi

FILE_NAME=$(basename -- "$FILE_PATH" .json)
DIR_NAME=$(dirname -- "$FILE_PATH")
SMALL_FILE="$DIR_NAME/$FILE_NAME.small.json"
jq ".[:$NUM_SAMPLES]" $FILE_PATH > $SMALL_FILE
