set -e

FILE_PATH=$1
FILE_NAME=$(basename -- "$FILE_PATH" .json)
DIR_NAME=$(dirname -- "$FILE_PATH")
#SMALL_FILE="$DIR_NAME/$FILE_NAME.small.json"
#jq ".[:$COUNT]" $FILE_PATH > $SMALL_FILE
jq -r '.[] | [.query, .db_id] | @tsv' $FILE_PATH > "$FILE_PATH".gold.txt
