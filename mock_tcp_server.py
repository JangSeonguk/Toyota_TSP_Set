"""
Mock TCP Server for Testing
Simulates the browser automation server without requiring browser/login
"""

import socket
import json
import sys
from typing import Dict, Any

from error_codes import ErrorCode, get_error_message
import logger


class MockTCPServer:
    """Mock TCP server for testing command/response flow"""

    def __init__(self, port: int):
        """
        Initialize mock TCP server

        Args:
            port: Port number to listen on
        """
        self.port = port
        self.server_socket = None
        self.is_running = False

    def start(self) -> bool:
        """
        Start mock TCP server

        Returns:
            True if server started successfully
        """
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', self.port))
            self.server_socket.listen(5)

            self.is_running = True
            logger.log_success(f"Mock TCP server started on port {self.port}")
            print(f"\n{'='*60}")
            print(f"Mock TCP Server Running on port {self.port}")
            print(f"{'='*60}")
            print("This is a TEST server that simulates responses")
            print("Press Ctrl+C to stop")
            print(f"{'='*60}\n")
            return True

        except Exception as e:
            logger.log_error(f"Failed to start mock server on port {self.port}", e)
            return False

    def handle_client(self, client_sock: socket.socket, client_addr: tuple):
        """
        Handle a single client connection

        Args:
            client_sock: Client socket
            client_addr: Client address tuple (host, port)
        """
        logger.log_info(f"Client connected from {client_addr[0]}:{client_addr[1]}")
        print(f"\n[{client_addr[0]}:{client_addr[1]}] Connected")

        try:
            # Receive command
            data = client_sock.recv(4096)

            if not data:
                print(f"[{client_addr[0]}:{client_addr[1]}] Disconnected (no data)")
                return

            command_str = data.decode('utf-8').strip()
            print(f"[{client_addr[0]}:{client_addr[1]}] Received {len(command_str)} bytes")

            # Parse JSON
            try:
                command = json.loads(command_str)
                print(f"[{client_addr[0]}:{client_addr[1]}] Command: {command.get('command', 'UNKNOWN')}")
            except json.JSONDecodeError as e:
                # Invalid JSON
                error_response = {
                    "result": "error",
                    "error_code": ErrorCode.INVALID_COMMAND_FORMAT.value,
                    "error_message": get_error_message(ErrorCode.INVALID_COMMAND_FORMAT, str(e))
                }
                self.send_response(client_sock, error_response)
                print(f"[{client_addr[0]}:{client_addr[1]}] Sent error: Invalid JSON")
                return

            # Process command
            response = self.process_command(command)
            self.send_response(client_sock, response)

            result = response.get('result', 'unknown')
            print(f"[{client_addr[0]}:{client_addr[1]}] Sent response: {result}")

        except Exception as e:
            logger.log_error(f"Error handling client {client_addr}", e)
            print(f"[{client_addr[0]}:{client_addr[1]}] Error: {e}")

        finally:
            client_sock.close()
            print(f"[{client_addr[0]}:{client_addr[1]}] Disconnected")

    def process_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process command and generate mock response

        Args:
            command: Command dictionary

        Returns:
            Response dictionary
        """
        command_type = command.get('command')

        # Validate command type
        if not command_type:
            return {
                "result": "error",
                "error_code": ErrorCode.INVALID_COMMAND_FORMAT.value,
                "error_message": get_error_message(ErrorCode.INVALID_COMMAND_FORMAT, "Missing 'command' field")
            }

        if command_type not in ['START', 'STOP']:
            return {
                "result": "error",
                "error_code": ErrorCode.INVALID_COMMAND_FORMAT.value,
                "error_message": get_error_message(ErrorCode.INVALID_COMMAND_FORMAT, f"Invalid command: {command_type}")
            }

        # Handle STOP command
        if command_type == 'STOP':
            print("\n[SERVER] STOP command received (mock server will continue running)")
            return {
                "result": "success",
                "message": "STOP command acknowledged (mock server)"
            }

        # Validate START command parameters
        required_params = ['id', 'password', 'vin', 'fname1', 'response_option']

        for param in required_params:
            if param not in command or command[param] is None:
                return {
                    "result": "error",
                    "error_code": ErrorCode.MISSING_REQUIRED_PARAMS.value,
                    "error_message": get_error_message(ErrorCode.MISSING_REQUIRED_PARAMS, f"Missing: {param}")
                }

        # Validate response_option
        response_option = command.get('response_option')
        if response_option not in [1, 2, 3]:
            return {
                "result": "error",
                "error_code": ErrorCode.INVALID_RESPONSE_OPTION.value,
                "error_message": get_error_message(ErrorCode.INVALID_RESPONSE_OPTION, f"Got: {response_option}")
            }

        # Validate option1 usage
        option1 = command.get('option1')
        if response_option == 2:
            if not option1:
                return {
                    "result": "error",
                    "error_code": ErrorCode.MISSING_REQUIRED_PARAMS.value,
                    "error_message": get_error_message(ErrorCode.MISSING_REQUIRED_PARAMS, "option1 required")
                }
        else:
            option1 = None

        # Validate fname2/response_option2/option2 consistency
        fname2 = command.get('fname2')
        option2 = command.get('option2')
        response_option2 = command.get('response_option2')

        if fname2:
            if response_option2 is None:
                response_option2 = response_option

            if response_option2 not in [1, 2, 3]:
                return {
                    "result": "error",
                    "error_code": ErrorCode.INVALID_RESPONSE_OPTION.value,
                    "error_message": get_error_message(ErrorCode.INVALID_RESPONSE_OPTION, f"Got: {response_option2}")
                }

            if response_option2 == 2:
                if not option2:
                    return {
                        "result": "error",
                        "error_code": ErrorCode.MISSING_REQUIRED_PARAMS.value,
                        "error_message": get_error_message(ErrorCode.MISSING_REQUIRED_PARAMS, "option2 required")
                    }
            else:
                option2 = None

        # Generate success response
        fnames = [command['fname1']]
        options = [option1]

        if fname2:
            fnames.append(fname2)
            options.append(option2)

        response = {
            "result": "success",
            "vin": command['vin'],
            "fnames": fnames,
            "response_type": response_option,
            "options": options,
            "timestamp": "2025-01-01T00:00:00.000Z",
            "mock": True
        }
        if fname2:
            response["response_type2"] = response_option2
        return response

    def send_response(self, sock: socket.socket, response: Dict[str, Any]):
        """
        Send response to client

        Args:
            sock: Client socket
            response: Response dictionary
        """
        try:
            response_json = json.dumps(response)
            sock.sendall(response_json.encode('utf-8'))
        except Exception as e:
            logger.log_error("Error sending response", e)

    def run(self):
        """Run the mock server (blocking)"""
        if not self.start():
            return

        try:
            while self.is_running:
                # Accept client connection
                client_sock, client_addr = self.server_socket.accept()

                # Handle client (blocking - one client at a time)
                self.handle_client(client_sock, client_addr)

        except KeyboardInterrupt:
            print("\n\n[SERVER] Shutting down...")
            logger.log_info("Mock server stopped by user")

        finally:
            self.stop()

    def stop(self):
        """Stop the mock server"""
        self.is_running = False
        if self.server_socket:
            try:
                self.server_socket.close()
                logger.log_success("Mock server stopped")
            except:
                pass


def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("Mock TCP Server for Testing")
        print("\nUsage:")
        print("  python mock_tcp_server.py [port]")
        print("\nExamples:")
        print("  python mock_tcp_server.py       - Start on default port 5000")
        print("  python mock_tcp_server.py 5001  - Start on port 5001")
        print("\nThis server simulates the browser automation server without")
        print("requiring browser/login. Use it to test TCP communication.")
        sys.exit(0)

    # Parse port
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000

    # Enable debug logging
    logger.enable_debug()

    # Create and run server
    server = MockTCPServer(port)
    server.run()


if __name__ == "__main__":
    main()
