#!/usr/bin/env python3
"""
Example script demonstrating how to use the mock HTTP server.

This script starts a mock HTTP server using example input and output files,
then sends a request to the server to demonstrate how it works.
"""

import json
import time
import requests
import threading
import argparse
from pathlib import Path

from src.mock_server import MockHTTPServer


def start_server(port, input_file=None, output_file=None, config_file=None):
    """Start the mock HTTP server in a separate thread."""
    if config_file:
        server = MockHTTPServer(
            config_file=config_file,
            port=port
        )
    elif input_file and output_file:
        server = MockHTTPServer(
            input_file=input_file,
            output_file=output_file,
            port=port
        )
    else:
        raise ValueError("Either config_file or both input_file and output_file must be provided")

    # Start the server in a separate thread
    server_thread = threading.Thread(target=server.start)
    server_thread.daemon = True  # This ensures the thread will exit when the main program exits
    server_thread.start()

    # Give the server a moment to start up
    time.sleep(1)

    return server_thread


def send_test_request(port, input_file=None, config_file=None):
    """Send a test request to the mock HTTP server."""
    # Determine which file to read the first request from
    if input_file:
        file_to_read = input_file
    elif config_file:
        # Read the config file to get the first input file
        with open(config_file, 'r') as f:
            config = json.load(f)
        file_pairs = config.get('file_pairs', [])
        if not file_pairs:
            print("No file pairs found in config file")
            return
        file_to_read = file_pairs[0].get('input')
        if not file_to_read:
            print("No input file found in the first file pair")
            return
    else:
        print("Either input_file or config_file must be provided")
        return

    # Read the first request from the file
    with open(file_to_read, 'r') as f:
        first_request = json.loads(f.readline())

    # Extract the URL and body from the first request
    url = f"http://localhost:{port}{first_request['url']}"
    body = first_request['body']

    print(f"Sending request to {url}")
    print(f"Request body: {json.dumps(body, indent=2)}")

    # Send the request
    response = requests.post(url, json=body)

    # Print the response
    print(f"Response status code: {response.status_code}")
    if response.status_code == 200:
        print(f"Response body: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Response text: {response.text}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run an example of the mock HTTP server')

    # Create a mutually exclusive group for input/output files vs config file
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--config', help='Path to the config file containing input/output file pairs')
    group.add_argument('--input', help='Path to the input JSONL file (requires --output)')

    parser.add_argument('--output', help='Path to the output JSONL file (required if --input is used)')
    parser.add_argument('--port', type=int, default=8888, help='Port to bind the server to')

    args = parser.parse_args()

    # Validate arguments
    if args.input and not args.output:
        parser.error("--output is required when --input is used")

    # Check file existence
    if args.config:
        config_path = Path(args.config)
        if not config_path.exists():
            print(f"Error: Config file {args.config} does not exist")
            exit(1)
    else:
        input_path = Path(args.input)
        output_path = Path(args.output)

        if not input_path.exists():
            print(f"Error: Input file {args.input} does not exist")
            exit(1)

        if not output_path.exists():
            print(f"Error: Output file {args.output} does not exist")
            exit(1)

    # Start the server
    if args.config:
        server_thread = start_server(port=args.port, config_file=args.config)
    else:
        server_thread = start_server(port=args.port, input_file=args.input, output_file=args.output)

    try:
        # Send a test request
        if args.config:
            send_test_request(port=args.port, config_file=args.config)
        else:
            send_test_request(port=args.port, input_file=args.input)
    except Exception as e:
        print(f"Error sending test request: {e}")

    # Keep the server running for a while to allow for manual testing
    try:
        print("\nServer is running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping server...")
