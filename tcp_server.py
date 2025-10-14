"""
TCP Server Module
Handles TCP connections and message transmission
"""

import socket
import json
import threading
from typing import Optional, Tuple, Dict, Any, Callable

import logger
from error_codes import ErrorCode, get_error_message


class TCPServer:
    """TCP Server for receiving commands and sending responses"""

    def __init__(self, port: int):
        """
        Initialize TCP server

        Args:
            port: Port number to listen on
        """
        self.port = port
        self.server_socket: Optional[socket.socket] = None
        self.client_socket: Optional[socket.socket] = None
        self.client_address: Optional[Tuple[str, int]] = None
        self.is_running = False
        self._lock = threading.Lock()

    def start(self) -> bool:
        """
        Start TCP server and begin listening

        Returns:
            True if server started successfully, False otherwise
        """
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Bind to all interfaces on specified port
            self.server_socket.bind(('0.0.0.0', self.port))
            self.server_socket.listen(1)  # Queue up to 1 connection

            self.is_running = True
            logger.log_success(f"TCP server started on port {self.port}")
            return True

        except Exception as e:
            logger.log_error(f"Failed to start TCP server on port {self.port}", e)
            return False

    def accept_connection(self, timeout: Optional[float] = None) -> bool:
        """
        Accept a single client connection (blocks until connection received)

        Args:
            timeout: Socket timeout in seconds (None = blocking)

        Returns:
            True if connection accepted, False on error
        """
        with self._lock:
            # Check if a client is already connected
            if self.client_socket is not None:
                logger.log_fail("Connection attempt rejected - client already connected")
                return False

        try:
            if timeout is not None:
                self.server_socket.settimeout(timeout)

            logger.log_info("Waiting for client connection...")
            client_sock, client_addr = self.server_socket.accept()

            with self._lock:
                self.client_socket = client_sock
                self.client_address = client_addr

            logger.log_success(f"Client connected from {client_addr[0]}:{client_addr[1]}")
            return True

        except socket.timeout:
            logger.log_info("Accept connection timeout")
            return False
        except Exception as e:
            logger.log_error("Error accepting connection", e)
            return False

    def receive_command(self, buffer_size: int = 4096) -> Optional[str]:
        """
        Receive command from connected client

        Args:
            buffer_size: Receive buffer size in bytes

        Returns:
            Command string or None on error
        """
        with self._lock:
            if self.client_socket is None:
                logger.log_fail("No client connected")
                return None

        try:
            # Receive data
            data = self.client_socket.recv(buffer_size)

            if not data:
                logger.log_info("Client disconnected")
                self.close_client_connection()
                return None

            command_str = data.decode('utf-8').strip()
            logger.log_info(f"Received {len(command_str)} bytes from client")
            return command_str

        except Exception as e:
            logger.log_error("Error receiving command", e)
            self.close_client_connection()
            return None

    def send_response(self, response_dict: Dict[str, Any]) -> bool:
        """
        Send response to connected client

        Args:
            response_dict: Response dictionary

        Returns:
            True if sent successfully, False on error
        """
        with self._lock:
            if self.client_socket is None:
                logger.log_fail("No client connected - cannot send response")
                return False

        try:
            # Convert to JSON
            response_json = json.dumps(response_dict)
            response_bytes = response_json.encode('utf-8')

            # Send response
            self.client_socket.sendall(response_bytes)
            logger.log_success(f"Response sent ({len(response_bytes)} bytes)")
            return True

        except Exception as e:
            logger.log_error("Error sending response", e)
            self.close_client_connection()
            return False

    def close_client_connection(self):
        """Close current client connection"""
        with self._lock:
            if self.client_socket is not None:
                try:
                    self.client_socket.close()
                    logger.log_info(f"Client connection closed: {self.client_address}")
                except:
                    pass
                finally:
                    self.client_socket = None
                    self.client_address = None

    def stop(self):
        """Stop TCP server and close all connections"""
        logger.log_info("Stopping TCP server...")

        self.is_running = False

        # Close client connection
        self.close_client_connection()

        # Close server socket
        if self.server_socket is not None:
            try:
                self.server_socket.close()
                logger.log_success("TCP server stopped")
            except:
                pass
            finally:
                self.server_socket = None

    def is_client_connected(self) -> bool:
        """
        Check if a client is currently connected

        Returns:
            True if client connected, False otherwise
        """
        with self._lock:
            return self.client_socket is not None


def send_error_to_client(sock: socket.socket, error_code: ErrorCode, detail: str = ""):
    """
    Send error message to a socket (for rejecting connections)

    Args:
        sock: Socket to send to
        error_code: ErrorCode enum value
        detail: Optional error detail
    """
    try:
        error_msg = get_error_message(error_code, detail)
        error_json = json.dumps({
            "result": "error",
            "error_code": error_code.value,
            "error_message": error_msg
        })
        sock.sendall(error_json.encode('utf-8'))
        sock.close()
    except:
        pass
