#run this first: chmod +x Evaluation_Run_DIN.sh
#then: ./Evaluation_Run_DIN.sh
# or source ./Evaluation_Run_DIN.sh if file is not executable

# A '/' is needed at the end of dataset path

set -e # Stop execution of the subsequent commands if one fails

source .venv/bin/activate

python3 ./run_data.py --model din \
--dataset models/din/sample_data/ \
--output din.pred.out \
--skip-run 

cat scores_mean.csv