# Implementing Custom Models

Implementing a custom model is simple, you just need to open the 
`src/mode/custom_predictor.py` and implement the `_run_internal` function.

In the following, interfaces that are available to help with the implementation 
are described.

The `CustomPredictor`has access to the protected property `_run_conf`.
This configuration includes all the information required to execute one 
iteration of the prediction. 
It has various properties such as iteration number, temperature, 
dataset configuration, etc.

Now we briefly explain the`DummyPredictor` to gain some idea on how a model should
be implemented.
```python linenums="1"
async def _run_internal(self):
    examples = load_data(self._run_conf.dataset_config.get_test_path()).to_dict("records")
    with open(self._run_conf.get_pred_path(), "w") as file:
        for i, example in enumerate(examples):
            sql = example['query']
            file.write(f"{sql}\n")
```

In the first line, entries of the test workload are loaded in the `examples` variable.
This function should read each example in the given file in order and generate a predicted
SQL, then write back the generated SQLs in a file. 
The total number of the lines in the file should be equal to the number of examples, one line
for each example. 
This procedure is the same for any model. The main logic of the prediction
corresponds to the line `sql = example['query']`.
Since, we are implementing a dummy predictor, it simply outputs the gold queries as the 
generated SQL. However, for a real text2SQL model, this line should be replaced with a 
function call that generates an SQL query for a given example, which includes the question,
db_id, etc.

The next section is devoted to other interfaces that are included in SQLyzr that enables 
easy implementation of an LLM-based text2SQL model.

## Batch File Programming Model

To use LLM APIs, and more specifically, the OpenAI's API, there are two options: standard API and batch API.
Standard API is used to send each request individually as a separate HTTP request.
However, with Batch API, multiple requests are written in a file, and then the file is submitted to OpenAI 
in order to be processed. The main benefit of BatchAPI is the reduced cost which is half of the price of standard
API.

In SQLyzr, we use a unified programming model for interacting with OpenAI, to avoid requiring developers 
writing separate programs based on whether Batch API is used or not. 
As a result, by using the SQLyzr programming model, users can switch between the standard and batch API 
at runtime without a need for a code-change.