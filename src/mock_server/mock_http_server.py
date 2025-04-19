import json
import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, List, Optional, Tuple, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MockHTTPRequestHandler(BaseHTTPRequestHandler):
    """
    HTTP request handler for the mock server.
    Matches incoming requests with requests in the input file and
    returns corresponding responses from the output file.
    """

    def __init__(self, *args, request_map=None, **kwargs):
        self.request_map = request_map or {}
        super().__init__(*args, **kwargs)

    def do_POST(self):
        """Handle POST requests."""
        content_length = int(self.headers.get('Content-Length', 0))
        request_body = self.rfile.read(content_length).decode('utf-8')

        try:
            custom_id = self.headers['custom_id']
            request_json = json.loads(request_body)
            response = self._find_matching_response(custom_id)

            if response:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
                logger.info(f"Matched request to {self.path} and sent response")
            else:
                self.send_response(404)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                error_msg = {"error": "No matching request found"}
                self.wfile.write(json.dumps(error_msg).encode('utf-8'))
                logger.warning(f"No matching request found for {self.path}")
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_msg = {"error": "Invalid JSON in request body"}
            self.wfile.write(json.dumps(error_msg).encode('utf-8'))
            logger.error("Invalid JSON in request body")

    def _find_matching_response(self, custom_id: str) -> Optional[Dict[str, Any]]:
        """
        Find a matching response for the given URL and request body.

        Args:
            url: The request URL
            request_body: The request body as a dictionary

        Returns:
            The matching response or None if no match is found
        """
        request_key = custom_id
        logger.info(f"Looking for response with custom_id: {custom_id}")

        return self.request_map.get(request_key)


class MockHTTPServer:
    """
    Mock HTTP server that reads input and output files and serves responses.
    """

    def __init__(self, input_file: str = None, output_file: str = None, config_file: str = None,
                 host: str = 'localhost', port: int = 8888):
        """
        Initialize the mock HTTP server.

        Args:
            input_file: Path to the input JSONL file (optional if config_file is provided)
            output_file: Path to the output JSONL file (optional if config_file is provided)
            config_file: Path to the config file containing input/output file pairs (optional if input_file and output_file are provided)
            host: Host to bind the server to
            port: Port to bind the server to
        """
        self.input_file = input_file
        self.output_file = output_file
        self.config_file = config_file
        self.host = host
        self.port = port
        self.request_map = {}
        handler = lambda *args, **kwargs: MockHTTPRequestHandler(*args, request_map=self.request_map, **kwargs)
        self.server = HTTPServer((self.host, self.port), handler)
        logger.info(f"Starting mock HTTP server on {self.host}:{self.port}")

    def load_data(self) -> None:
        """Load data from input and output files or from a config file."""
        if self.config_file:
            self._load_from_config()
        elif self.input_file and self.output_file:
            self._load_from_files(self.input_file, self.output_file)
        else:
            logger.error("Either config_file or both input_file and output_file must be provided")
            raise ValueError("Either config_file or both input_file and output_file must be provided")

        logger.info(f"Loaded {len(self.request_map)} request-response pairs")

    def _load_from_config(self) -> None:
        """Load data from a config file containing input/output file pairs."""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)

            file_pairs = config.get('file_pairs', [])
            if not file_pairs:
                logger.warning("No file pairs found in config file")
                return

            for pair in file_pairs:
                input_file = pair.get('input')
                output_file = pair.get('output')

                if input_file and output_file:
                    self._load_from_files(input_file, output_file)
                else:
                    logger.warning(f"Skipping invalid file pair: {pair}")
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
            raise

    def _load_from_files(self, input_file: str, output_file: str) -> None:
        """Load data from input and output files."""
        input_data = self._load_jsonl(input_file)
        output_data = self._load_jsonl(output_file)

        if len(input_data) != len(output_data):
            logger.warning(
                f"Input file {input_file} has {len(input_data)} entries but output file {output_file} has {len(output_data)} entries")

        for i, request in enumerate(input_data):
            if i < len(output_data):
                self.request_map[request['custom_id']] = output_data[i]

    def _load_jsonl(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Load data from a JSONL file.

        Args:
            file_path: Path to the JSONL file

        Returns:
            List of dictionaries parsed from the JSONL file
        """
        data = []
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line:  # Skip empty lines
                    try:
                        data.append(json.loads(line))
                    except json.JSONDecodeError:
                        logger.error(f"Failed to parse JSON from line: {line}")
        return data

    def _make_hashable(self, request: Dict[str, Any]) -> Any:
        """
        Convert a request dictionary to a hashable representation for use as a dictionary key.

        Args:
            request: The request dictionary

        Returns:
            A hashable representation of the request (either the custom_id or a tuple)
        """
        # Check if the request has a custom_id
        custom_id = request.get('custom_id')

        if custom_id:
            # If the request has a custom_id, use it as the key
            logger.info(f"Using custom_id as key: {custom_id}")
            return custom_id
        else:
            # Fall back to the old method if no custom_id is present
            method = request.get('method', '')
            url = request.get('url', '')
            body = json.dumps(request.get('body', {}), sort_keys=True)
            logger.info(f"No custom_id found, using method, URL, and body as key")
            return (method, url, body)

    def start(self) -> None:
        """Start the mock HTTP server."""
        # Load data before starting the server
        self.load_data()

        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            logger.info("Shutting down mock HTTP server")
            self.server.server_close()

    def stop(self):
        self.server.server_close()


def main():
    """Main entry point for the mock HTTP server."""
    parser = argparse.ArgumentParser(description='Start a mock HTTP server')

    # Create a mutually exclusive group for input/output files vs config file
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--config', help='Path to the config file containing input/output file pairs')
    parser.add_argument('--host', default='localhost', help='Host to bind the server to')
    parser.add_argument('--port', type=int, default=8888, help='Port to bind the server to')

    args = parser.parse_args()

    server = MockHTTPServer(config_file=args.config, host=args.host, port=args.port)

    server.start()


if __name__ == '__main__':
    main()
