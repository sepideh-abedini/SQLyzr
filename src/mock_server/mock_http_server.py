import json
import argparse
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, List, Optional, Tuple, Any, Set
import logging

from src.configs.config_loader import load_config, ConfigData
from src.configs.sqlyzr_config import SQLyzrConfig
from src.sqlyzr.sqlyzr import Sqlyzr
from src.util.file_utils import read_json
from src.util.model_utils import read_jsonl

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
from pathlib import Path


def jsonl_in_out_pairs(directory: str):
    dir_path = Path(directory)
    pairs = []

    for infile in dir_path.glob("*.in*.jsonl"):
        outfile = infile.with_name(infile.name.replace(".in.", ".out."))
        if outfile.exists():
            pairs.append((infile, outfile))

    return pairs


class MockHTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, request_map=None, **kwargs):
        self.request_map = request_map or {}
        super().__init__(*args, **kwargs)

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        request_body = self.rfile.read(content_length).decode('utf-8')

        try:
            custom_id = self.headers['custom_id']
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
        request_key = custom_id
        logger.info(f"Looking for response with custom_id: {custom_id}")
        return self.request_map.get(request_key)


class MockHTTPServer:
    def __init__(self, mock_data_dir: str, conf: str, host: str = 'localhost', port: int = 8888):
        self.mock_data_dir = mock_data_dir
        self.conf = load_config(conf)
        self.host = host
        self.port = port
        self.request_map = {}
        handler = lambda *args, **kwargs: MockHTTPRequestHandler(*args, request_map=self.request_map, **kwargs)
        self.server = HTTPServer((self.host, self.port), handler)
        logger.info(f"Starting mock HTTP server on {self.host}:{self.port}")

    def load_data(self) -> None:
        logger.info("Loading data from data dir")
        data_dirs = set()
        for c in self.conf.eval_conf.get_run_confs():
            p = Path(c.get_pred_path().replace(self.conf.eval_conf.base_dir, self.mock_data_dir))
            data_dirs.add(p.parent)

        for d in self.conf.eval_conf.datasets:
            p = os.path.join(self.mock_data_dir, "aug", d)
            data_dirs.add(p)

        logger.info(f"Lookup Dirs: {data_dirs}")

        all_paris = set()
        for d in data_dirs:
            pairs = jsonl_in_out_pairs(d)
            all_paris.update(pairs)
            logger.info(f"Pairs Found: {pairs}")

        self.load_pairs(all_paris)

        logger.info(f"Loaded {len(self.request_map)} request-response pairs")

    def load_pairs(self, pairs: Set[Tuple[Path, Path]]) -> None:
        if len(pairs) == 0:
            raise RuntimeError("No pairs found")

        for pair in pairs:
            input_file = pair[0]
            output_file = pair[1]
            logger.info(f"Loading data from {input_file} and {output_file}")

            if input_file and output_file:
                self.load_pair(input_file, output_file)

    def load_pair(self, input_file: Path, output_file: Path) -> None:
        input_data = read_jsonl(input_file.as_posix())
        output_data = read_jsonl(output_file.as_posix())

        if len(input_data) != len(output_data):
            raise RuntimeError(f"Input and output files have different lengths {len(input_data)} != {len(output_data)}")

        for i, request in enumerate(input_data):
            self.request_map[request['custom_id']] = output_data[i]

    def start(self) -> None:
        self.load_data()
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            logger.info("Shutting down mock HTTP server")
            self.server.server_close()

    def stop(self):
        self.server.shutdown()
        self.server.server_close()


def main():
    parser = argparse.ArgumentParser(description='Start a mock HTTP server')
    parser.add_argument('--config', help='Path to the config file containing input/output file pairs')
    parser.add_argument('--host', default='localhost', help='Host to bind the server to')
    parser.add_argument('--port', type=int, default=8888, help='Port to bind the server to')

    args = parser.parse_args()

    server = MockHTTPServer(conf=args.config, host=args.host, port=args.port)

    server.start()


if __name__ == '__main__':
    main()
