A=$1
B=$2
OUT=$3
jq -r -s '.[0] + .[1]' $A $B > $OUT