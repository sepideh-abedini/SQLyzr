- [SQLyzer](#sqlyzer)
    - [How to Run](#how-to-run)
        - [Installing requirements](#installing-requirements)
        - [Running SQLyzer](#running-sqlyzer)
        - [Configuration](#configuration)
        - [Extras](#extras)
            - [Generating BNF Grammar](#generating-bnf-grammar)
            - [Tests](#tests)
    - [Input Format](#input-format)
    - [Pre-Processing](#pre-processing)
    - [Parsing](#parsing)
    - [Processing](#processing)
        - [Properties Processor](#properties-processor)
        - [Graph Drawer](#graph-drawer)
        - [Category Processor](#category-processor)
- [Reading Next](#reading-next)
    - [How it Works?](#how-it-works)
    - [Category Assignment](#category-assignment)

# SQLyzer

## How to Run

Basically, the program reads SQL queries from the
input file and exports several dataframes as CSV files
as a result of different processing done on the SQLs.

### Installing requirements

```shell
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

### Running Evaluator

Following script runs the execution evaluation on the
prediction file and exports the evaluation result alongside
the category of the gold SQL:

```bash
python3 eval.py -i "data/models/din/results.csv" \
                -o "out/eval.csv" \
                -d "data/datasets/spider/database"
```

#### Options

- `-i, --input`: Prediction results csv, should include columns: `PREDICTED SQL`,`GOLD SQL`,`DATABASE`
- `-o, --output`: Output file
- `-d, --db`: Database dir

### Running SQLyzer

First, ensure that `spider` dataset exists in `data/datasets/spider`:

```
.
├── data
│   ├── datasets
│   │   ├── spider
│   │   │   ├── database
│   │   │   ├── dev.json
│   │   │   └── tables.json
```

Now you can run the program:

```shell
python3 main.py --preprocess --props --graph --cats
```

> Graph processor takes around 30s on spider dev.

#### Options

- `-r, --preprocess`: Convert `dev.json` to `sql.csv`
- `-p, --props`: Extract the props into `props.csv`
- `-g, --graph`: Save syntax tree of each statement in `out/graphs`
- `-c, --cats`: Extract the categories into `cats.csv`
- `-s, --samples`: Run the processors only on the first `k` statements

### Configuration

Configuration can be made using [`config.py`](config.py) file.
For example, the path to the spider dataset or name of
the processor output file can be set.

#### Input Format

SQLyzer accepts input as a CSV file with two columns:

- `sql`: Select statement strings
- `db_id`: database id of the given SQL

Furthermore, `table.json` and a `database` directory
containing the actual database files matching the
`db_id`s are required for extracting some properties.

### Extras

#### Generating BNF Grammar

The following program generates the BNF grammar
based on the rules defined in [parser](src/sql_parser/parser.py).

```shell
python3 gen_grammar.py
```

#### Tests

Execute the following command to run the tests:

```shell
python3 -m pytest
```


## Pre-Processing

A pre-processing step is needed to convert a dataset's
data into a proper input format of SQLyzer.
For example, [`SpiderProcessor`](src/batch/spider_pre_processor.py) converts the `dev.json`
file into a CSV file with `sql` and `db_id` columns.

## Parsing

After reading the input, each SQL string is parsed and
an object of type [`SqlAstNode`](src/sql_parser/node.py) is created which will
be used for further processing.

## Processing

After parsing, a processor applies a specific processing
on each statement (e.g. drawing syntax tree, extracting properties) and exports
the results as CSV file.
Currently, there are three processors:

### Properties Processor

This processor extract several properties from a given SQL statement.
It then exports the result as a CSV file.
Extracted properties include:

- Maximum nest level
- Binary operators used
- Tables used

### Graph Drawer

This processor draws the syntax tree of a select statement.
It exports the tree as a `png` file.
It helps to visualize the structure of statements and
especially finding out the problems of parser.

### Category Processor

This processor assigns a category to each statement,
the output is a CSV file containing the SQL string
and the name of the category assigned to the statement.

# Reading Next

### [How it Works?](docs/Readme.md)

This link contains implementation details.

### [Category Assignment](docs/Category.md)

This link contains category assignment procedure. 



# Useful Links

### [SQLite Syntax](https://www.sqlite.org/lang_select.html)

### [PLY Documentation](http://www.dabeaz.com/ply/ply.html)












