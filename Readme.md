# SQLyzr: Comprehensive Text-to-SQL Benchmarking Framework

## Table of Contents

- [Native Installation](#native-installation)
- [Configuration](#configuration)
- [Benchmark Data](#benchmark-data)
    - [Sample Data](#sample-data)
    - [Full benchmark data](#full-benchmark-data)
- [Integrating custom model](#integrating-custom-model)

## Native Installation

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/)
1. Install dependencies

```shell
uv sync
source .venv/bin/activate
```

3. Setup env variables:

```shell
cp .env.txt .env
```

3. Fill in the empty env variables.

3. Setup config file:

```shell
cp confs/conf.json .
```

> Refer to [configuration](#configuration) for the description of configration options.

5. Run SQLyzr:

```shell
python3 main.py
```

6. Check the output files generated in the `out` directory.
   For instance, if you use the provided configuration, a plot for overall comparison of the models is
   generated saved in `out/custom_small_spider/charts/Model/overall__scores.png`.

7. Cleanup output directory:

```shell
rm -rf out
```

## Configuration

The configuration file controls the pipeline execution, model selection, and evaluation parameters.
For each option, you can use the values listed below:

- `dataset`: Dataset to run the experiments:
    - `spider`: [Spider Benchmark](https://yale-lily.github.io/spider)
    - `bird`: [Bird Benchmark](https://bird-bench.github.io/)
    - `beaver`: [Beaver benchmark](https://github.com/peterbaile/beaver)
    - `sqlyzr`: All of the above combined
- `dataset_size`: Size of dataset to run the experiments:
    - `full`
    - `small`: A small sample of `full`
- `models`: List of models to evaluate:
    - `din`:  [DIN-SQL](https://github.com/mohammadrezapourreza/few-shot-nl2sql-with-prompting)
    - `dail`: [DAIL-SQL] [dail](https://github.com/BeachWang/DAIL-SQL)
    - `custom`: The option to use if you want to integrate a custom model. See details [here](./docs/Custom-Model.md)
- `itrs`: The number of iterations to run the evaluation.
- `temps`: A list of LLM temperature values
- `pipeline`: Enabled/Disabled status for each pipeline stage
    - `scale`: Scale databases using scaling factors specified by the `scales` option
    - `verify`: Validate the input dataset format
    - `predict`: Run Text2SQL models to generate SQL queries
    - `eval`: Execute queries and compute evaluation scores
    - `charts`: Generate evaluation plots based for the scores computed in the `eval` stage
    - `analysis`: Generate error-fixing suggestions for incorrect queries
    - `augment`: Generate new datapoints for the sub-categories with accuracy below the threshold specified by
      `error_threshold`
- `aug_per_sub_cat`: Number of new datapoints to be generated for each sub-category with score below the threshold
  specified by `error_threshold`
- `batch`: use batch API
- `charts`: List of the charts to be generated:
    - `Overall`: Avg score for all metrics in a single plot
    - `Execution Accuracy`
    - `Relaxed Execution Accuracy`: Relaxed version of execution accuracy
    - `Exact Match`: For definition see section 6 [here](https://arxiv.org/pdf/1809.08887)
    - `Execution Time`: Execution time of predicted queries
    - `Gold Execution Time`: Execution time of gold queries
    - `Token Usage`: Embedding tokens used by LLM to predict queries
    - `Category Distribution`: Distribution of queries across [categories](https://demo.sqlyzr.site/categories)
- `error_threshold`: The threshold for augmentation. New data-points are generated for each sub-category with an
  accuracy below this threshold.
- `force`: Force pipeline to ignore the existing files and rerun all steps
- `options.llm`: The LLM model to use for SQL generation (currently configuration only used by the `custom` model).

> ‼️⚠️ Only if you don't need any data inside the `out` directory ⚠️‼️

### Verify datasets

To verify each dataset, making sure it has the correct format, you can run the following command:
```shell
PYTHONPATH=. python3 scripts/verify_data.py -d <dataset> -s <dataset_size>
```
For instance, you can use the following command to verify the `spider` `small` dataset:
```shell
PYTHONPATH=. python3 scripts/verify_data.py -d spider -s small
```

## Benchmark Data

### Sample Data

The `sample_data` directory is included in the repository and
includes small samples of the SPIDER, BIRD, and BEAVER datasets.
Using this data you can experiment with SQLyzr and make sure that
your setup is working.

### Full benchmark data

Download the complete benchmark data [here]().

After download extract the zip file as the `data` directory.
Expected working directory structure:

```
repo
├── data
│ ├── beaver
│ ├── bird
│ └── spider
```

You also need to set the following environment variable (inside the `.env` file):

```shell
SQLYZR_DATA_DIR=data
```

#### Beaver Benchmark

One of the included benchmarks is Bevaer. However, in contrast
to Spider and BIRD that use SQLite, Beaver uses MySQL.
To bringup a MySQL server on your machine and enable evaluation
of Beaver workload, use the following command:

> Note that to use Beaver you should download the full benchmark data.

```shell
docker compose up -d
```

this command starts a MySQL container with Bevaer data included.

> The database initialization might take long, since the whole
> dump of the Beaver benchmark is being inserted into the database.

## Integrating custom model

SQLyzr allows integration of custom Text-to-SQL models.
The `custom` model already included in the repository is a simple model
that prompts LLM with the user question and database schema to generate
a SQL query.
This model is included to demonstrate how custom models can be implemented.
You can either customize the prompt your implement a model from scratch.
Read [here](./docs/Custom-Model.md) for more details on the implementation of custom models.

By implementing a custom model you can also benefit from seamless switch
between batch mode and synchronous mode.
By using the `batch` option in configuration, you can switch between
these two modes at runtime, and you don't need two separate implementations
for these modes.
