
usage() {
  echo "Usage $0 [-o out_file] json_1 json_2 ..."
  echo "Appends the files sequentially and write them to out_file"
  exit 1
}

while getopts "o:" opt; do
    case $opt in
        o) OUT_FILE=$OPTARG ;;
        *) usage ;;
    esac
done

if [ -z "$OUT_FILE" ]; then
    usage
fi

shift $((OPTIND - 1))

jq -r -s 'add' "$@" > $OUT_FILE