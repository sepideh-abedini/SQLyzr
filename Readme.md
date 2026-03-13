# SQLyzr: Comprehensive Text-to-SQL Benchmarking Framework

## Native Installation

```shell
python3.11 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```
### Getting started

1. Setup env variables:

```shell
cp .env.txt .env
```

2. Setup experiment data:
```shell
cp -r sample_data data
```

3. Fill in the empty env variables.

3. Setup config file:

```shell
cp confs/conf.json .
```

> Refer to [configuration](#configuration) for the description of configration options.

5. Cleanup output directory:

```shell
rm -rf out
```

> ‼️⚠️ Only if you don't need any data inside the `out` directory ⚠️‼️

6. Run SQLyzr:

```shell
python3 main.py
```

7. Check the output files generated in the `out` directory.
   For instance, a plot for overall comparison of the models is
   generated in `out/din_spider_small/charts/overall.png`.

### Configuration

The configuration file controls the pipeline execution, model selection, and evaluation parameters.

- `aug_per_sub_cat`: Number of new datapoints to be generated for each sub-category that has accuracy lower than the
  `error_threshold`.
- `batch`: use batch API
- `charts`: List of the charts to be generated:
- `dataset`: Dataset to run the experiments:
    - `spider`
    - `bird`
    - `agg`: Both spider and bird
- `dataset_size`: Size of dataset to run the experiments:
    - `small`
    - `all`
- `error_threshold`: The threshold for augmentation. New data-points are generated for each sub-category with an
  accuracy below this threshold.
- `force`: Force pipeline to ignore the existing files and rerun all steps
- `itrs`: The number of iterations to run the evaluation.
- `models`: List of models to evaluate:
    - `din`
    - `dail`
- `pipeline`: Enabled/Disabled status for each step of the pipeline
    - `verify`: Validate the input dataset format
    - `predict`: Run Text2SQL models to generate SQL queries
    - `eval`: Execute queries and compute evaluation scores
    - `charts`: Generate the plots
    - `transformers`: Generate error-fixing suggestions
    - `augment`: Generate new datapoints for the sub-categories with accuracy below the threshold
- `temps`: A list of LLM temperature values

### Sample Data

The `sample_data` directory includes small samples of the BIRD
and SPIDER datasets.
Using this data you can verify that SQLyzr is working properly.
