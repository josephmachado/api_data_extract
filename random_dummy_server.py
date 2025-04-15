from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import json
import random


class RateLimitHandler(BaseHTTPRequestHandler):
    # Class variables to track the last request timestamp and next wait time
    last_request_time = 0
    next_rate_limit = random.randint(
        2, 5
    )  # Initial random rate limit between 2- 5 seconds

    def do_GET(self):
        """Handle GET requests"""
        current_time = time.time()
        time_since_last_request = current_time - self.__class__.last_request_time

        # Check if the request is for the API endpoint
        if self.path == "/api":
            # Check if enough time has passed since the last request
            if time_since_last_request < self.__class__.next_rate_limit:
                # Rate limit exceeded
                wait_time = self.__class__.next_rate_limit - time_since_last_request
                self.send_response(429)  # Too Many Requests
                self.send_header("Content-type", "application/json")
                self.send_header("Retry-After", str(int(wait_time)))
                self.end_headers()
                response = {
                    "status": "error",
                    "message": f"Rate limit exceeded. Try again in {wait_time:.2f} seconds.Rate limited at {self.next_rate_limit} calls per second ",
                    "retry_after": int(wait_time),
                    "rate_limit": f"Rate limited at {self.next_rate_limit} calls per second",
                }
                self.wfile.write(json.dumps(response).encode())
            else:
                # Process the request, update the last request time, and set a new random rate limit
                self.__class__.last_request_time = current_time
                # Generate a new random rate limit for the next request
                self.__class__.next_rate_limit = random.randint(10, 30)
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                response = {
                    "status": "success",
                    "message": f"API request processed successfully Rate limited at {self.next_rate_limit} calls per second ",
                    "timestamp": current_time,
                    "rate_limit": f"Rate limited at {self.next_rate_limit} calls per second",
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
    print(f"API is rate limited to 1 request every 2-5 seconds (randomized)")
    print("Access the API at http://localhost:8000/api")
    httpd.serve_forever()


if __name__ == "__main__":
    run_server()
