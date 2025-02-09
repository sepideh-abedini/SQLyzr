INPUT=$1
OUTPUT=$2
jq -r 'map (.table_names_original = .table_name_original, .table_names = .table_names_original)' $INPUT > $OUTPUT
