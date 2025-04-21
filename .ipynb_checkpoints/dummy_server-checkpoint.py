# Written by Claude
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import json


class RateLimitHandler(BaseHTTPRequestHandler):
    # Class variable to track the last request timestamp
    last_request_time = 0
    rate_limit_seconds = 10

    def do_GET(self):
        """Handle GET requests"""
        current_time = time.time()
        time_since_last_request = current_time - self.__class__.last_request_time

        # Check if the request is for the API endpoint
        if self.path == "/api":
            # Check if enough time has passed since the last request
            if time_since_last_request < self.__class__.rate_limit_seconds:
                # Rate limit exceeded
                wait_time = self.__class__.rate_limit_seconds - time_since_last_request
                self.send_response(429)  # Too Many Requests
                self.send_header("Content-type", "application/json")
                self.send_header("Retry-After", str(int(wait_time)))
                self.end_headers()
                response = {
                    "status": "error",
                    "message": f"Rate limit exceeded. Try again in {wait_time:.2f} seconds.",
                    "retry_after": int(wait_time),
                }
                self.wfile.write(json.dumps(response).encode())
            else:
                # Process the request and update the last request time
                self.__class__.last_request_time = current_time
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                response = {
                    "status": "success",
                    "message": "API request processed successfully",
                    "timestamp": current_time,
                }
                self.wfile.write(json.dumps(response).encode())
        else:
            # For any other path, return 404
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = {"status": "error", "message": "Not found"}
            self.wfile.write(json.dumps(response).encode())

    # Handle POST requests the same way
    def do_POST(self):
        self.do_GET()


def run_server(host="localhost", port=8000):
    """Start the HTTP server"""
    server_address = (host, port)
    httpd = HTTPServer(server_address, RateLimitHandler)
    print(f"Starting server on {host}:{port}")
    print(
        f"API is rate limited to 1 request every {RateLimitHandler.rate_limit_seconds} seconds"
    )
    print("Access the API at http://localhost:8000/api")
    httpd.serve_forever()


if __name__ == "__main__":
    run_server()
