INPUT=$1
OUTPUT=$2
jq -r 'map (.query = .sql)' $INPUT > $OUTPUT