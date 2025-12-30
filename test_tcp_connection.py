"""
TCP Connection Test Client
Tests TCP server connectivity and command/response flow
"""

import socket
import json
import sys
import time
from typing import Dict, Any, Optional


def test_connection(host: str, port: int, timeout: float = 5.0) -> bool:
    """
    Test basic TCP connection to server

    Args:
        host: Server hostname or IP
        port: Server port
        timeout: Connection timeout in seconds

    Returns:
        True if connection successful
    """
    print(f"\n{'='*60}")
    print(f"TEST 1: Connection Test")
    print(f"{'='*60}")
    print(f"Attempting to connect to {host}:{port}...")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))
        print(f"[PASS] Connection successful!")
        sock.close()
        return True
    except socket.timeout:
        print(f"[FAIL] Connection timeout after {timeout} seconds")
        return False
    except ConnectionRefusedError:
        print(f"[FAIL] Connection refused - is the server running?")
        return False
    except Exception as e:
        print(f"[FAIL] Connection failed: {type(e).__name__}: {e}")
        return False


def send_and_receive(host: str, port: int, command: Dict[str, Any],
                     timeout: float = 30.0) -> Optional[Dict[str, Any]]:
    """
    Send command and receive response

    Args:
        host: Server hostname or IP
        port: Server port
        command: Command dictionary
        timeout: Socket timeout in seconds

    Returns:
        Response dictionary or None on error
    """
    try:
        # Create socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)

        # Connect
        print(f"\nConnecting to {host}:{port}...")
        sock.connect((host, port))
        print("[OK] Connected")

        # Send command
        command_json = json.dumps(command)
        print(f"\nSending command ({len(command_json)} bytes):")
        print(json.dumps(command, indent=2))

        sock.sendall(command_json.encode('utf-8'))
        print("[OK] Command sent")

        # Receive response
        print(f"\nWaiting for response (timeout: {timeout}s)...")
        response_data = sock.recv(8192)

        if not response_data:
            print("[FAIL] No response received")
            sock.close()
            return None

        print(f"[OK] Received {len(response_data)} bytes")

        # Parse response
        response_json = response_data.decode('utf-8')
        response = json.loads(response_json)

        print("\nResponse:")
        print(json.dumps(response, indent=2))

        sock.close()
        return response

    except socket.timeout:
        print(f"[FAIL] Socket timeout after {timeout} seconds")
        return None
    except ConnectionRefusedError:
        print("[FAIL] Connection refused - is the server running?")
        return None
    except json.JSONDecodeError as e:
        print(f"[FAIL] Failed to parse response JSON: {e}")
        return None
    except Exception as e:
        print(f"[FAIL] Error: {type(e).__name__}: {e}")
        return None


def test_invalid_json(host: str, port: int) -> bool:
    """
    Test server's handling of invalid JSON

    Args:
        host: Server hostname or IP
        port: Server port

    Returns:
        True if server handled error correctly
    """
    print(f"\n{'='*60}")
    print(f"TEST 2: Invalid JSON Test")
    print(f"{'='*60}")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        sock.connect((host, port))

        # Send invalid JSON
        invalid_json = "{invalid json}"
        print(f"Sending invalid JSON: {invalid_json}")
        sock.sendall(invalid_json.encode('utf-8'))

        # Receive error response
        response_data = sock.recv(4096)
        response = json.loads(response_data.decode('utf-8'))

        print("\nResponse:")
        print(json.dumps(response, indent=2))

        sock.close()

        # Check if error response
        if response.get('result') == 'error':
            print("[PASS] Server correctly returned error response")
            return True
        else:
            print("[FAIL] Server did not return expected error response")
            return False

    except Exception as e:
        print(f"[FAIL] Test failed: {type(e).__name__}: {e}")
        return False


def test_missing_params(host: str, port: int) -> bool:
    """
    Test server's validation of missing parameters

    Args:
        host: Server hostname or IP
        port: Server port

    Returns:
        True if server handled error correctly
    """
    print(f"\n{'='*60}")
    print(f"TEST 3: Missing Parameters Test")
    print(f"{'='*60}")

    # Command with missing required parameters
    command = {
        "command": "START",
        "id": "test_user"
        # Missing: password, vin, fname1, response_option
    }

    response = send_and_receive(host, port, command, timeout=5.0)

    if response and response.get('result') == 'error':
        error_code = response.get('error_code')
        if error_code == 1004:  # MISSING_REQUIRED_PARAMS
            print("\n[PASS] Server correctly detected missing parameters")
            return True
        else:
            print(f"\n[FAIL] Unexpected error code: {error_code}")
            return False
    else:
        print("\n[FAIL] Server did not return expected error")
        return False


def test_stop_command(host: str, port: int) -> bool:
    """
    Test STOP command (does not actually stop the server in this test)

    Args:
        host: Server hostname or IP
        port: Server port

    Returns:
        True if command accepted
    """
    print(f"\n{'='*60}")
    print(f"TEST 4: STOP Command Test")
    print(f"{'='*60}")
    print("Note: This test sends STOP but server may continue running")

    command = {
        "command": "STOP"
    }

    response = send_and_receive(host, port, command, timeout=5.0)

    if response:
        print("\n[PASS] STOP command accepted")
        return True
    else:
        print("\n[FAIL] STOP command failed")
        return False


def test_malformed_start_command(host: str, port: int) -> bool:
    """
    Test START command with invalid response_option

    Args:
        host: Server hostname or IP
        port: Server port

    Returns:
        True if server handled error correctly
    """
    print(f"\n{'='*60}")
    print(f"TEST 5: Invalid Response Option Test")
    print(f"{'='*60}")

    command = {
        "command": "START",
        "id": "test_user",
        "password": "test_pass",
        "vin": "TEST123",
        "fname1": "TEST_FUNC",
        "response_option": 99,  # Invalid
        "option1": "TEST"
    }

    response = send_and_receive(host, port, command, timeout=5.0)

    if response and response.get('result') == 'error':
        error_code = response.get('error_code')
        if error_code == 1007:  # INVALID_RESPONSE_OPTION
            print("\n[PASS] Server correctly detected invalid response_option")
            return True
        else:
            print(f"\n[FAIL] Unexpected error code: {error_code}")
            return False
    else:
        print("\n[FAIL] Server did not return expected error")
        return False


def run_all_tests(host: str = 'localhost', port: int = 5000):
    """
    Run all TCP connection tests

    Args:
        host: Server hostname or IP
        port: Server port
    """
    print("\n" + "="*60)
    print("TCP SERVER TEST SUITE")
    print("="*60)
    print(f"Target: {host}:{port}")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    tests = [
        ("Connection Test", lambda: test_connection(host, port)),
        ("Invalid JSON Test", lambda: test_invalid_json(host, port)),
        ("Missing Parameters Test", lambda: test_missing_params(host, port)),
        ("Invalid Response Option Test", lambda: test_malformed_start_command(host, port)),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n[FAIL] Test crashed: {type(e).__name__}: {e}")
            results.append((test_name, False))

        # Small delay between tests
        time.sleep(0.5)

    # Print summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")

    passed = 0
    failed = 0

    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status:10} {test_name}")
        if result:
            passed += 1
        else:
            failed += 1

    print(f"\nTotal: {len(results)} | Passed: {passed} | Failed: {failed}")

    if failed == 0:
        print("\n*** All tests passed! ***")
    else:
        print(f"\n*** WARNING: {failed} test(s) failed ***")

    return failed == 0


def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("Usage:")
        print("  python test_tcp_connection.py              - Run all tests (localhost:5000)")
        print("  python test_tcp_connection.py <host> <port> - Run tests on custom host/port")
        print("\nExamples:")
        print("  python test_tcp_connection.py")
        print("  python test_tcp_connection.py localhost 5000")
        print("  python test_tcp_connection.py 192.168.1.100 5000")
        sys.exit(0)

    # Parse arguments
    host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5000

    # Run tests
    success = run_all_tests(host, port)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
