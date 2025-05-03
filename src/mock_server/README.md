# Mock HTTP Server

A simple mock HTTP server that can be used for testing HTTP clients without making actual API calls.

## Features

- Matches requests based on custom ID for reliable request-response pairing
- Supports multiple input/output file pairs via a config file
- Default port is 8888 and host is localhost
- Fallback to method, URL, and body matching if custom ID is not present

## Usage

### Using a Config File

```bash
python -m src.mock_server.mock_http_server --config path/to/config.json
```

Or using the example script:

```bash
python -m src.mock_server.example --config path/to/config.json
```

### Using Individual Input/Output Files

```bash
python -m src.mock_server.mock_http_server --input path/to/input.jsonl --output path/to/output.jsonl
```

Or using the example script:

```bash
python -m src.mock_server.example --input path/to/input.jsonl --output path/to/output.jsonl
```

## Config File Format

The config file should be a JSON file with the following structure:

```json
{
  "file_pairs": [
    {
      "input": "path/to/input1.jsonl",
      "output": "path/to/output1.jsonl"
    },
    {
      "input": "path/to/input2.jsonl",
      "output": "path/to/output2.jsonl"
    }
  ]
}
```

## Input File Format

The input file should be a JSONL file where each line is a JSON object representing a request. Each request should have a `custom_id` field for matching:

```json
{"custom_id":"request1","method":"POST","url":"/api/endpoint","body":{"key":"value"}}
```

## Output File Format

The output file should be a JSONL file where each line is a JSON object representing a response:

```json
{"id":"response1","result":{"key":"value"}}
```

## Request Matching

The server matches incoming requests with stored responses using the following logic:

1. If the incoming request has a `custom_id` field, it uses that for matching
2. If no `custom_id` is present, it falls back to matching based on method, URL, and request body

## Example

See `example.py` for a complete example of how to use the mock server.

## Command Line Options

### Mock HTTP Server

- `--config`: Path to the config file containing input/output file pairs
- `--input`: Path to the input JSONL file (requires `--output`)
- `--output`: Path to the output JSONL file (required if `--input` is used)
- `--host`: Host to bind the server to (default: localhost)
- `--port`: Port to bind the server to (default: 8888)

### Example Script

- `--config`: Path to the config file containing input/output file pairs
- `--input`: Path to the input JSONL file (requires `--output`)
- `--output`: Path to the output JSONL file (required if `--input` is used)
- `--port`: Port to bind the server to (default: 8888)