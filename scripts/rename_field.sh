set -eo pipefail

usage() {
  echo "Usage $0 [-i input_file] [-f field] [-n new_field]"
  echo "Renames the field to new_field in the given file"
  exit 1
}

while getopts "f:i:n:" opt; do
    case $opt in
        f) FIELD=$OPTARG ;;
        i) INPUT_FILE=$OPTARG ;;
        n) NEW_FIELD=$OPTARG ;;
        *) usage ;;
    esac
done

if [ -z "$INPUT_FILE" ] || [ -z "$FIELD" ] || [ -z "$NEW_FIELD" ]; then
    usage
fi

#jq -r "map (.$NEW_FIELD = .$FIELD | del(.$FIELD))" $INPUT_FILE > $INPUT_FILE.tmp
jq -r "map (.$NEW_FIELD = .$FIELD)" $INPUT_FILE > $INPUT_FILE.tmp
mv $INPUT_FILE.tmp $INPUT_FILE
