### How to run?

#### Installing requirements

```shell
python3.11 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

#### Prepare Data

Copy the spider dataset into data directory.
Make you have the following directories and files:

```shell
├── .env
├── data
│   └── spider
│       ├── database
│       ├── dev.json
│       └── tables.json
```
To create the `.env` file, duplicate the `.env.example`
and fill the variables.

Create sample data (only 8 entires) using the
following command:

```shell
cd data
./sample_dev.sh
```

It will create the following files:

```shell
├── data
│   └── spider
│       ├── dev.small.json
│       ├── dev.small.gold.txt
```

#### Run the SQLyzr with small data

```shell

export $(cat .env | xargs)
export PYTHONPATH=.
python3 main.py
```

