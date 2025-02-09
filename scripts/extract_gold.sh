set -eo pipefail


usage() {
  echo "Usage $0 [-i input_file]"
  echo "Extracts the SQL and db_id from given file write them to a file with .gold.txt suffix"
  exit 1
}

while getopts "i:" opt; do
  case $opt in
    i) FILE_PATH=$OPTARG;;
    *) usage ;;
  esac
done

if [ -z "$FILE_PATH" ]; then
    usage
fi

FILE_NAME=$(basename -- "$FILE_PATH" .json)
DIR_NAME=$(dirname -- "$FILE_PATH")
jq -r '.[] | [.query, .db_id] | @tsv' $FILE_PATH > "$FILE_PATH".gold.txt
