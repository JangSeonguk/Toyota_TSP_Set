"""
TSP Auto Interactive TCP Client
Connects to tsp_auto server and sends multiple commands in a session

Usage:
    python tsp_client.py [--host HOST] [--port PORT]
    python tsp_client.py --file <json_file>
    python tsp_client.py --interactive

Examples:
    # Interactive mode (default)
    python tsp_client.py

    # Send single JSON file
    python tsp_client.py --file start_command.json

    # Connect to custom host/port
    python tsp_client.py --host 192.168.1.100 --port 5000
"""

import socket
import json
import sys
import os
import argparse
import threading
import time
from typing import Optional, Dict, Any


class TSPClient:
    """Interactive TCP Client for TSP Auto server"""

    def __init__(self, host: str = 'localhost', port: int = 5000):
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.session_active = False

    def connect(self) -> bool:
        """Connect to server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            print(f"[OK] Connected to {self.host}:{self.port}")
            return True
        except ConnectionRefusedError:
            print(f"[ERROR] Connection refused. Is the server running on {self.host}:{self.port}?")
            return False
        except Exception as e:
            print(f"[ERROR] Connection failed: {e}")
            return False

    def disconnect(self):
        """Disconnect from server"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        self.connected = False
        self.session_active = False
        print("[OK] Disconnected")

    def send_command(self, command: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send command and receive response"""
        if not self.connected or not self.socket:
            print("[ERROR] Not connected to server")
            return None

        try:
            # Send command
            command_json = json.dumps(command)
            self.socket.sendall(command_json.encode('utf-8'))
            print(f"\n[SENT] {command.get('command')} command ({len(command_json)} bytes)")

            # Receive response
            self.socket.settimeout(120)  # 2 minute timeout for long operations
            response_data = self.socket.recv(8192)

            if not response_data:
                print("[ERROR] No response received (server disconnected)")
                self.connected = False
                return None

            response = json.loads(response_data.decode('utf-8'))
            self._print_response(response)

            # Track session state
            if command.get('command') == 'START' and response.get('add_request'):
                self.session_active = True
                print(f"\n[SESSION] add_request mode active (use CLOSE to end)")
            elif command.get('command') == 'CLOSE':
                self.session_active = False
                print("\n[SESSION] Session closed")

            return response

        except socket.timeout:
            print("[ERROR] Response timeout")
            return None
        except Exception as e:
            print(f"[ERROR] {type(e).__name__}: {e}")
            return None

    def _print_response(self, response: Dict[str, Any]):
        """Print formatted response"""
        result = response.get('result', 'unknown')

        print("\n" + "=" * 50)
        if result == 'success':
            print(f"[SUCCESS] {response.get('command', 'START')}")
            print("-" * 50)

            # Command-specific output
            cmd = response.get('command')
            if cmd == 'SET':
                print(f"  VIN: {response.get('vin')}")
                print(f"  fname: {response.get('fname')}")
                print(f"  response_option: {response.get('response_option')}")
                if response.get('option'):
                    print(f"  option: {response.get('option')}")
            elif cmd == 'PUSH':
                print(f"  VIN: {response.get('vin')}")
                print(f"  topic: {response.get('topic')}")
                print(f"  push_template: {response.get('push_template')}")
            elif cmd == 'CLOSE':
                print(f"  message: {response.get('message')}")
                if response.get('vin'):
                    print(f"  VIN: {response.get('vin')}")
            else:
                # START response
                print(f"  VIN: {response.get('vin')}")
                print(f"  fnames: {', '.join(response.get('fnames', []))}")
                print(f"  response_type: {response.get('response_type')}")
                if response.get('add_request'):
                    print(f"  add_request: {response.get('add_request')}")

        else:
            print(f"[ERROR] Code {response.get('error_code')}")
            print("-" * 50)
            print(f"  message: {response.get('error_message')}")

        print(f"  timestamp: {response.get('timestamp')}")
        print("=" * 50)

    def send_file(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Load and send command from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                command = json.load(f)
            print(f"[LOAD] {filepath}")
            print(f"       Command: {command.get('command')}")
            return self.send_command(command)
        except FileNotFoundError:
            print(f"[ERROR] File not found: {filepath}")
            return None
        except json.JSONDecodeError as e:
            print(f"[ERROR] Invalid JSON: {e}")
            return None

    def interactive_mode(self):
        """Run interactive command loop"""
        print("\n" + "=" * 60)
        print("TSP AUTO - Interactive Client")
        print("=" * 60)
        print("Commands:")
        print("  load <file.json>  - Load and send JSON file")
        print("  send <json>       - Send inline JSON")
        print("  set               - Quick SET command")
        print("  push              - Quick PUSH command")
        print("  close             - Send CLOSE command")
        print("  status            - Show connection status")
        print("  reconnect         - Reconnect to server")
        print("  quit              - Exit client")
        print("=" * 60)

        while True:
            try:
                # Show prompt with session status
                session_indicator = "[SESSION] " if self.session_active else ""
                connected_indicator = "+" if self.connected else "-"
                prompt = f"\n{session_indicator}[{connected_indicator}] > "

                user_input = input(prompt).strip()

                if not user_input:
                    continue

                parts = user_input.split(maxsplit=1)
                cmd = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""

                if cmd == 'quit' or cmd == 'exit' or cmd == 'q':
                    print("Exiting...")
                    break

                elif cmd == 'status':
                    self._show_status()

                elif cmd == 'reconnect':
                    self.disconnect()
                    self.connect()

                elif cmd == 'load':
                    if not args:
                        print("Usage: load <file.json>")
                        continue
                    if not self.connected:
                        print("[ERROR] Not connected. Use 'reconnect' first.")
                        continue
                    self.send_file(args)

                elif cmd == 'send':
                    if not args:
                        print("Usage: send <json>")
                        print('Example: send {"command": "CLOSE"}')
                        continue
                    if not self.connected:
                        print("[ERROR] Not connected. Use 'reconnect' first.")
                        continue
                    try:
                        command = json.loads(args)
                        self.send_command(command)
                    except json.JSONDecodeError as e:
                        print(f"[ERROR] Invalid JSON: {e}")

                elif cmd == 'close':
                    if not self.connected:
                        print("[ERROR] Not connected.")
                        continue
                    self.send_command({"command": "CLOSE"})

                elif cmd == 'set':
                    if not self.connected:
                        print("[ERROR] Not connected.")
                        continue
                    self._quick_set()

                elif cmd == 'push':
                    if not self.connected:
                        print("[ERROR] Not connected.")
                        continue
                    self._quick_push()

                elif cmd == 'help':
                    self._show_help()

                else:
                    # Try to parse as JSON directly
                    try:
                        command = json.loads(user_input)
                        if self.connected:
                            self.send_command(command)
                        else:
                            print("[ERROR] Not connected. Use 'reconnect' first.")
                    except json.JSONDecodeError:
                        print(f"Unknown command: {cmd}")
                        print("Type 'help' for available commands")

            except KeyboardInterrupt:
                print("\nUse 'quit' to exit")
            except EOFError:
                break

        self.disconnect()

    def _show_status(self):
        """Show connection status"""
        print("\n--- Status ---")
        print(f"  Server: {self.host}:{self.port}")
        print(f"  Connected: {self.connected}")
        print(f"  Session Active: {self.session_active}")
        print("--------------")

    def _show_help(self):
        """Show help message"""
        print("""
Commands:
  load <file.json>  - Load and send JSON file
  send <json>       - Send inline JSON
  set               - Interactive SET command builder
  push              - Interactive PUSH command builder
  close             - Send CLOSE command
  status            - Show connection status
  reconnect         - Reconnect to server
  quit              - Exit client

You can also paste raw JSON directly at the prompt.

Example JSON commands:
  {"command": "CLOSE"}
  {"command": "SET", "fname": "CSU_ACN", "response_option": 1}
  {"command": "PUSH", "topic": "doorlock", "push_template": "CYCL_AHCVT_CMD"}
""")

    def _quick_set(self):
        """Interactive SET command builder"""
        print("\n--- SET Command ---")
        try:
            fname = input("  fname: ").strip()
            if not fname:
                print("Cancelled")
                return

            response_option = input("  response_option (1/2/3): ").strip()
            response_option = int(response_option)

            command = {
                "command": "SET",
                "fname": fname,
                "response_option": response_option
            }

            if response_option == 2:
                option = input("  option: ").strip()
                command["option"] = option

            self.send_command(command)
        except (ValueError, KeyboardInterrupt):
            print("Cancelled")

    def _quick_push(self):
        """Interactive PUSH command builder"""
        print("\n--- PUSH Command ---")
        try:
            topic = input("  topic: ").strip()
            if not topic:
                print("Cancelled")
                return

            push_template = input("  push_template: ").strip()
            if not push_template:
                print("Cancelled")
                return

            command = {
                "command": "PUSH",
                "topic": topic,
                "push_template": push_template
            }

            self.send_command(command)
        except KeyboardInterrupt:
            print("Cancelled")


def main():
    parser = argparse.ArgumentParser(
        description='TSP Auto Interactive TCP Client',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Interactive mode (default):
    python tsp_client.py

  Send single JSON file:
    python tsp_client.py --file start_command.json

  Custom server:
    python tsp_client.py --host 192.168.1.100 --port 5000

  Send file to custom server:
    python tsp_client.py --host 192.168.1.100 --file command.json
        """
    )

    parser.add_argument('--host', default='localhost',
                        help='Server hostname (default: localhost)')
    parser.add_argument('--port', type=int, default=5000,
                        help='Server port (default: 5000)')
    parser.add_argument('--file', '-f', dest='json_file',
                        help='JSON file to send (single command mode)')
    parser.add_argument('--interactive', '-i', action='store_true',
                        help='Force interactive mode after file send')

    args = parser.parse_args()

    # Create client
    client = TSPClient(args.host, args.port)

    # Connect to server
    if not client.connect():
        sys.exit(1)

    try:
        if args.json_file:
            # Send file
            response = client.send_file(args.json_file)

            # If add_request mode, enter interactive mode
            if response and response.get('add_request'):
                print("\n[INFO] Entering interactive mode for add_request session...")
                client.interactive_mode()
            elif args.interactive:
                client.interactive_mode()
            else:
                result = 0 if response and response.get('result') == 'success' else 1
                sys.exit(result)
        else:
            # Interactive mode
            client.interactive_mode()

    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
