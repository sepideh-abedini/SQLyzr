INPUT=$1
OUTPUT=$2
jq -r 'map (.query = .SQL)' $INPUT > $OUTPUT
