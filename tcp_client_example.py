"""
TCP Client for TSP Auto
Sends JSON command file to tsp_auto.exe server

Usage:
    python tcp_client_example.py <json_file_path>

Example:
    python tcp_client_example.py example_command.json
"""

import socket
import json
import sys
import os


def send_command(host: str, port: int, command: dict) -> dict:
    """
    Send command to TCP server and receive response

    Args:
        host: Server hostname or IP
        port: Server port
        command: Command dictionary

    Returns:
        Response dictionary
    """
    try:
        # Create socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server
            print(f"Connecting to {host}:{port}...")
            sock.connect((host, port))
            print("Connected!")

            # Send command
            command_json = json.dumps(command)
            print(f"\nSending command ({len(command_json)} bytes):")
            print(json.dumps(command, indent=2))

            sock.sendall(command_json.encode('utf-8'))

            # Receive response
            print("\nWaiting for response...")
            response_data = sock.recv(8192)

            if not response_data:
                print("No response received")
                return None

            response_json = response_data.decode('utf-8')
            response = json.loads(response_json)

            print(f"\nReceived response ({len(response_data)} bytes):")
            print(json.dumps(response, indent=2))

            return response

    except ConnectionRefusedError:
        print(f"ERROR: Connection refused. Is the server running on {host}:{port}?")
        return None
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        return None


def load_command_from_file(filepath: str) -> dict:
    """
    Load command from JSON file

    Args:
        filepath: Path to JSON file

    Returns:
        Command dictionary
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            command = json.load(f)
        return command
    except FileNotFoundError:
        print(f"ERROR: File not found: {filepath}")
        return None
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in file: {e}")
        return None




def main():
    """Main entry point"""
    # Check arguments
    if len(sys.argv) != 2:
        print("Usage:")
        print("  python tcp_client_example.py <json_file_path>")
        print("")
        print("Example:")
        print("  python tcp_client_example.py example_command.json")
        print("  python tcp_client_example.py C:\\path\\to\\command.json")
        sys.exit(1)

    json_file_path = sys.argv[1]

    # Server configuration
    HOST = 'localhost'
    PORT = 5000

    # Check if file exists
    if not os.path.exists(json_file_path):
        print(f"ERROR: File not found: {json_file_path}")
        sys.exit(1)

    # Load command from JSON file
    print("=" * 60)
    print("TSP AUTO - TCP CLIENT")
    print("=" * 60)
    print(f"JSON File: {json_file_path}")
    print(f"Server: {HOST}:{PORT}")
    print("=" * 60)

    command = load_command_from_file(json_file_path)

    if not command:
        print("\nFailed to load JSON file")
        sys.exit(1)

    # Send command to server
    response = send_command(HOST, PORT, command)

    # Display result
    if response:
        print("\n" + "=" * 60)
        if response.get('result') == 'success':
            print("SUCCESS")
            print("=" * 60)
            print(f"VIN: {response.get('vin')}")
            print(f"Functions: {', '.join(response.get('fnames', []))}")
            print(f"Response Type: {response.get('response_type')}")
            if response.get('response_type2') is not None:
                print(f"Response Type 2: {response.get('response_type2')}")
            print(f"Options: {', '.join(response.get('options', []))}")
            print(f"Timestamp: {response.get('timestamp')}")
        else:
            print("ERROR")
            print("=" * 60)
            print(f"Error Code: {response.get('error_code')}")
            print(f"Error Message: {response.get('error_message')}")
            if response.get('detail'):
                print(f"Detail: {response.get('detail')}")
        print("=" * 60)
        sys.exit(0 if response.get('result') == 'success' else 1)
    else:
        print("\nFailed to communicate with server")
        sys.exit(1)


if __name__ == "__main__":
    main()
