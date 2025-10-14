"""
TCP Client Example
Demonstrates how to send commands to the browser automation module via TCP

Usage Examples:
    # Send a START command with test data
    python tcp_client_example.py test

    # Send a real START command (edit the script first!)
    python tcp_client_example.py start

    # Send a STOP command
    python tcp_client_example.py stop

    # Send a custom command from JSON file
    python tcp_client_example.py custom <json_file>

    # Interactive mode
    python tcp_client_example.py interactive
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


def interactive_mode(host: str, port: int):
    """
    Interactive mode for building and sending commands

    Args:
        host: Server hostname or IP
        port: Server port
    """
    print("\n" + "=" * 60)
    print("INTERACTIVE MODE")
    print("=" * 60)

    # Choose command type
    print("\nSelect command type:")
    print("  1. START - Begin automation")
    print("  2. STOP - Stop server")
    choice = input("Enter choice (1-2): ").strip()

    if choice == "2":
        command = {"command": "STOP"}
        print("\nSending STOP command...")
        send_command(host, port, command)
        return

    if choice != "1":
        print("Invalid choice")
        return

    # Build START command
    print("\n" + "-" * 60)
    print("Building START command")
    print("-" * 60)

    user_id = input("Enter username: ").strip()
    password = input("Enter password: ").strip()
    vin = input("Enter VIN: ").strip()
    fname1 = input("Enter primary function name (fname1): ").strip()

    fname2_input = input("Enter secondary function name (fname2) [optional, press Enter to skip]: ").strip()
    fname2 = fname2_input if fname2_input else None

    print("\nResponse options:")
    print("  1 - Default response")
    print("  2 - Custom response (requires option value)")
    print("  3 - No response")
    response_option = int(input("Enter response option (1-3): ").strip())

    option1 = None
    option2 = None

    if response_option == 2:
        option1 = input("Enter option1 value (for fname1): ").strip()
        if fname2:
            option2 = input("Enter option2 value (for fname2): ").strip()
    elif response_option == 1:
        option1 = "ACK"  # Default value
        if fname2:
            option2 = "ACK"

    # Build command
    command = {
        "command": "START",
        "id": user_id,
        "password": password,
        "vin": vin,
        "fname1": fname1,
        "fname2": fname2,
        "response_option": response_option,
        "option1": option1,
        "option2": option2
    }

    print("\n" + "-" * 60)
    print("Command to send:")
    print(json.dumps(command, indent=2))
    print("-" * 60)

    confirm = input("\nSend this command? (y/n): ").strip().lower()
    if confirm == 'y':
        send_command(host, port, command)
    else:
        print("Cancelled")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python tcp_client_example.py start         - Send START command (edit script first!)")
        print("  python tcp_client_example.py stop          - Send STOP command")
        print("  python tcp_client_example.py test          - Send test START command")
        print("  python tcp_client_example.py custom <file> - Send command from JSON file")
        print("  python tcp_client_example.py interactive   - Interactive mode")
        sys.exit(1)

    command_type = sys.argv[1].lower()

    # Server configuration
    HOST = 'localhost'
    PORT = 5000

    if command_type == 'start':
        # Example START command
        # NOTE: Replace these values with actual credentials and data
        command = {
            "command": "START",
            "id": "your_username",
            "password": "your_password",
            "vin": "KMHXX00XXXX000000",
            "fname1": "CSU_ACN",
            "fname2": None,  # Optional
            "response_option": 1,  # 1=default, 2=custom, 3=no_response
            "option1": "ACK",
            "option2": None  # Required if fname2 provided and response_option=2
        }

        print("=" * 60)
        print("SENDING START COMMAND")
        print("=" * 60)
        response = send_command(HOST, PORT, command)

        if response:
            if response.get('result') == 'success':
                print("\n" + "=" * 60)
                print("SUCCESS!")
                print("=" * 60)
                print(f"VIN: {response.get('vin')}")
                print(f"Functions: {', '.join(response.get('fnames', []))}")
                print(f"Response Type: {response.get('response_type')}")
                print(f"Options: {', '.join(response.get('options', []))}")
            else:
                print("\n" + "=" * 60)
                print("ERROR!")
                print("=" * 60)
                print(f"Error Code: {response.get('error_code')}")
                print(f"Error Message: {response.get('error_message')}")

    elif command_type == 'stop':
        # STOP command
        command = {
            "command": "STOP"
        }

        print("=" * 60)
        print("SENDING STOP COMMAND")
        print("=" * 60)
        response = send_command(HOST, PORT, command)

        if response:
            print("\nServer is stopping...")

    elif command_type == 'test':
        # Test command with mock data
        command = {
            "command": "START",
            "id": "test_user",
            "password": "test_pass",
            "vin": "TEST123456789",
            "fname1": "TEST_FUNCTION",
            "fname2": None,
            "response_option": 1,
            "option1": "TEST",
            "option2": None
        }

        print("=" * 60)
        print("SENDING TEST COMMAND (will likely fail - test data)")
        print("=" * 60)
        response = send_command(HOST, PORT, command)

        if response:
            print(f"\nResult: {response.get('result')}")

    elif command_type == 'custom':
        # Load command from file
        if len(sys.argv) < 3:
            print("ERROR: Please specify JSON file path")
            print("Usage: python tcp_client_example.py custom <json_file>")
            sys.exit(1)

        filepath = sys.argv[2]
        command = load_command_from_file(filepath)

        if command:
            print("=" * 60)
            print("SENDING CUSTOM COMMAND FROM FILE")
            print("=" * 60)
            response = send_command(HOST, PORT, command)

            if response:
                print(f"\nResult: {response.get('result')}")

    elif command_type == 'interactive':
        # Interactive mode
        interactive_mode(HOST, PORT)

    else:
        print(f"Unknown command type: {command_type}")
        print("Use 'start', 'stop', 'test', 'custom', or 'interactive'")
        sys.exit(1)


if __name__ == "__main__":
    main()
