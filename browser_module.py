"""
TCP-Controlled Web Browser Automation Module
Main entry point for the automation system
"""

import argparse
import socket
import sys
import threading
import time
from typing import Optional, Dict, Any

import config
import logger
import browser_manager
import automation_workflow
import response_handler
import session_manager
from tcp_server import TCPServer
from command_processor import CommandQueue, validate_command, parse_command_json
from error_codes import ErrorCode


def parse_arguments():
    """
    Parse command-line arguments for both TCP mode and command-line mode

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='TCP-Controlled Web Browser Automation Module',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  TCP Mode:
    tsp_auto.exe --port 5000 --debug

  Command-Line Mode:
    tsp_auto.exe --id lge_1 --password xxx --vin KMHXX00XXXX000000
                 --fname1 CSU_ACN --response 1 --opt1 ACK --debug
        '''
    )

    # TCP Mode arguments
    parser.add_argument(
        '--port',
        type=int,
        default=config.DEFAULT_TCP_PORT,
        help=f'TCP port to listen on (default: {config.DEFAULT_TCP_PORT})'
    )

    # Command-Line Mode arguments
    parser.add_argument(
        '--id',
        type=str,
        help='Login ID (command-line mode)'
    )

    parser.add_argument(
        '--password',
        type=str,
        help='Login password (command-line mode)'
    )

    parser.add_argument(
        '--vin',
        type=str,
        help='VIN search term (command-line mode)'
    )

    parser.add_argument(
        '--fname1',
        type=str,
        help='Primary function name (command-line mode)'
    )

    parser.add_argument(
        '--fname2',
        type=str,
        default=None,
        help='Secondary function name (optional, command-line mode)'
    )

    parser.add_argument(
        '--response',
        type=int,
        choices=[1, 2, 3],
        help='Response option: 1=default, 2=custom, 3=no_response (command-line mode)'
    )

    parser.add_argument(
        '--response2',
        type=int,
        choices=[1, 2, 3],
        default=None,
        help='Response option for fname2: 1=default, 2=custom, 3=no_response (command-line mode)'
    )

    parser.add_argument(
        '--opt1',
        type=str,
        help='Type value for fname1 when response=2 (command-line mode)'
    )

    parser.add_argument(
        '--opt2',
        type=str,
        default=None,
        help='Type value for fname2 when response=2 (optional, command-line mode)'
    )

    # Debug flag
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging to console'
    )

    args = parser.parse_args()

    # Validate command-line mode requirements
    if args.id and args.password:
        # Command-line mode
        required_cli_args = ['vin', 'fname1', 'response']
        missing_args = [arg for arg in required_cli_args if not getattr(args, arg)]

        if missing_args:
            parser.error(f"Command-line mode requires: --id, --password, --vin, --fname1, --response. Missing: {', --'.join(missing_args)}")

        # Validate response option 2 requires opt1
        if args.response == 2 and not args.opt1:
            parser.error("--opt1 is required when --response is 2")

        if args.response in [1, 3]:
            args.opt1 = None

        # Default response2 to response when fname2 is provided
        if args.fname2 and args.response2 is None:
            args.response2 = args.response

        # Validate fname2 requires opt2 if response2 is 2
        if args.fname2 and args.response2 == 2 and not args.opt2:
            parser.error("--opt2 is required when --fname2 is provided and --response2 is 2")

        if args.response2 in [1, 3]:
            args.opt2 = None

    return args


def is_command_line_mode(args: argparse.Namespace) -> bool:
    """
    Check if running in command-line mode vs TCP mode

    Args:
        args: Parsed command-line arguments

    Returns:
        True if command-line mode, False if TCP mode
    """
    return args.id is not None and args.password is not None


def run_command_line_mode(args: argparse.Namespace):
    """
    Execute automation in command-line mode (without TCP server)

    Args:
        args: Parsed command-line arguments
    """
    logger.log_info("Starting command-line mode")
    logger.log_info(f"VIN: {args.vin}, Function: {args.fname1}, Response Option: {args.response}")

    try:
        # Build command dictionary from arguments
        command_data = {
            'command': 'START',
            'id': args.id,
            'password': args.password,
            'vin': args.vin,
            'fname1': args.fname1,
            'fname2': args.fname2,
            'response_option': args.response,
            'response_option2': args.response2,
            'option1': args.opt1,
            'option2': args.opt2
        }

        # Execute automation workflow
        success, result_data, error_code = automation_workflow.execute_automation(command_data)

        # Generate response
        if success:
            response = response_handler.create_success_response(
                result_data['vin'],
                result_data['fnames'],
                result_data['response_type'],
                result_data['options'],
                result_data.get('response_type2')
            )
        else:
            response = response_handler.create_error_response(error_code)

        # Display response
        print(response_handler.format_response_for_display(response))
        print("\nJSON Response:")
        print(response_handler.response_to_json(response))

        # Wait 15 seconds before cleanup to allow user to verify results
        if success:
            import time
            logger.log_info("Waiting 15 seconds before cleanup (to allow result verification)...")
            time.sleep(15)

        # Return appropriate exit code
        sys.exit(0 if success else 1)

    except Exception as e:
        logger.log_error("Error in command-line mode", e)
        response = response_handler.create_error_response(ErrorCode.COMMAND_PROCESSING_ERROR, str(e))
        print(response_handler.format_response_for_display(response))

        # Wait briefly before cleanup even on error
        import time
        logger.log_info("Waiting 5 seconds before cleanup...")
        time.sleep(5)

        sys.exit(1)
    finally:
        # Clean up browser
        logger.log_info("Cleaning up browser...")
        browser_manager.stop_browser()


def process_command_worker(command_queue: CommandQueue, tcp_server: TCPServer, stop_event: threading.Event):
    """
    Worker thread to process commands from queue

    Args:
        command_queue: Command queue
        tcp_server: TCP server instance
        stop_event: Event to signal worker to stop
    """
    logger.log_info("Command processor worker started")

    while not stop_event.is_set():
        try:
            # Try to get command from queue with timeout
            try:
                command = command_queue.dequeue(block=True, timeout=1.0)
            except:
                # Timeout - check stop event and continue
                continue

            logger.log_info(f"Processing command: {command.get('command')}")

            # Handle STOP command
            if command.get('command') == 'STOP':
                logger.log_info("STOP command received")
                # Close any active session
                session_manager.close_session()
                response = response_handler.create_success_response(
                    vin="N/A",
                    fnames=[],
                    response_type=0,
                    options=[],
                    response_type2=None
                )
                response['message'] = 'Stopping server'
                response['command'] = 'STOP'
                tcp_server.send_response(response)
                stop_event.set()
                break

            # Handle START command
            if command.get('command') == 'START':
                # Execute automation
                success, result_data, error_code = automation_workflow.execute_automation(command)

                # Generate response
                if success:
                    response = response_handler.create_success_response(
                        result_data['vin'],
                        result_data['fnames'],
                        result_data['response_type'],
                        result_data['options'],
                        result_data.get('response_type2')
                    )
                    response['command'] = 'START'

                    # Check if add_request mode is enabled
                    add_request = command.get('add_request', False)
                    if add_request:
                        vin = result_data['vin']
                        # Start session for add_request mode (no timeout)
                        session_manager.start_session(vin)
                        response['add_request'] = True
                        logger.log_info(f"add_request mode enabled: VIN={vin}")
                else:
                    response = response_handler.create_error_response(error_code)

                # Send response
                tcp_server.send_response(response)

                # Close browser if add_request is not enabled
                if not command.get('add_request', False):
                    logger.log_info("add_request disabled: closing browser")
                    browser_manager.stop_browser()

            # Handle SET command
            elif command.get('command') == 'SET':
                success, result_data, error_code = automation_workflow.execute_set_command(command)

                if success:
                    response = response_handler.create_set_response(
                        result_data['vin'],
                        result_data['fname'],
                        result_data['response_option'],
                        result_data.get('option')
                    )
                else:
                    response = response_handler.create_error_response(error_code)

                tcp_server.send_response(response)

            # Handle PUSH command
            elif command.get('command') == 'PUSH':
                success, result_data, error_code = automation_workflow.execute_push_command(command)

                if success:
                    if result_data.get('push_type'):
                        # push_type mode
                        response = response_handler.create_push_response(
                            result_data['vin'],
                            push_type=result_data['push_type'],
                            steps_completed=result_data['steps_completed']
                        )
                    else:
                        # Legacy mode
                        response = response_handler.create_push_response(
                            result_data['vin'],
                            topic=result_data['topic'],
                            push_template=result_data['push_template']
                        )
                else:
                    response = response_handler.create_error_response(error_code)

                tcp_server.send_response(response)

            # Handle CLOSE command
            elif command.get('command') == 'CLOSE':
                vin = session_manager.get_stored_vin()
                success, result_data, error_code = automation_workflow.execute_close_command()

                if success:
                    response = response_handler.create_close_response(vin)
                else:
                    response = response_handler.create_error_response(error_code)

                tcp_server.send_response(response)

        except Exception as e:
            logger.log_error("Error in command processor worker", e)
            try:
                error_response = response_handler.create_error_response(
                    ErrorCode.COMMAND_PROCESSING_ERROR,
                    str(e)
                )
                tcp_server.send_response(error_response)
            except:
                pass

    logger.log_info("Command processor worker stopped")


def run_tcp_mode(args: argparse.Namespace):
    """
    Start TCP server and listen for commands

    Args:
        args: Parsed command-line arguments
    """
    logger.log_info(f"Starting TCP server on port {args.port}")

    # Create TCP server
    tcp_server = TCPServer(args.port)

    if not tcp_server.start():
        logger.log_fail("Failed to start TCP server")
        sys.exit(1)

    # Create command queue
    command_queue = CommandQueue()

    # Create stop event for worker thread
    stop_event = threading.Event()

    # Start worker thread
    worker_thread = threading.Thread(
        target=process_command_worker,
        args=(command_queue, tcp_server, stop_event),
        daemon=True
    )
    worker_thread.start()

    try:
        # Main loop: accept connection, receive commands, enqueue
        while not stop_event.is_set():
            # Accept a client connection
            logger.log_info("Waiting for client connection...")
            if not tcp_server.accept_connection(timeout=1.0):
                continue

            # Process commands from this client
            while tcp_server.is_client_connected() and not stop_event.is_set():
                # Receive command (blocking until command received)
                try:
                    command_str = tcp_server.receive_command(timeout=5.0)
                except socket.timeout:
                    # No command received - continue waiting
                    continue

                if command_str is None:
                    # Client disconnected or error
                    break

                # Parse JSON
                command_dict, error_code, error_detail = parse_command_json(command_str)

                if command_dict is None:
                    # JSON parse error
                    error_response = response_handler.create_error_response(
                        error_code,
                        error_detail
                    )
                    tcp_server.send_response(error_response)
                    continue

                # Validate command
                is_valid, error_code, error_detail = validate_command(command_dict)

                if not is_valid:
                    # Validation error
                    error_response = response_handler.create_error_response(
                        error_code,
                        error_detail
                    )
                    tcp_server.send_response(error_response)
                    continue

                # Check for session-dependent commands without active session
                cmd_type = command_dict.get('command')
                if cmd_type in ['SET', 'PUSH'] and not session_manager.is_session_active():
                    error_response = response_handler.create_error_response(
                        ErrorCode.NO_ACTIVE_SESSION,
                        f"No active session for {cmd_type} command"
                    )
                    tcp_server.send_response(error_response)
                    continue

                # Enqueue command for processing
                command_queue.enqueue(command_dict)

                # If STOP command, wait for worker to finish and exit
                if command_dict.get('command') == 'STOP':
                    logger.log_info("STOP command enqueued, waiting for completion")
                    stop_event.wait(timeout=30)
                    break

                # If CLOSE command, session will be closed by worker
                if command_dict.get('command') == 'CLOSE':
                    logger.log_info("CLOSE command enqueued")

    except KeyboardInterrupt:
        logger.log_info("TCP server interrupted by user")
    finally:
        logger.log_info("Shutting down TCP server...")
        stop_event.set()
        # Close any active session
        session_manager.close_session()
        worker_thread.join(timeout=5)
        tcp_server.stop()
        browser_manager.stop_browser()
        logger.log_success("TCP server shut down complete")


def main():
    """Main entry point"""
    args = parse_arguments()

    # Enable debug logging if requested
    if args.debug:
        logger.enable_debug()
        config.DEBUG_MODE = True
        logger.log_info("Debug logging enabled")

    try:
        if is_command_line_mode(args):
            run_command_line_mode(args)
        else:
            run_tcp_mode(args)
    except KeyboardInterrupt:
        logger.log_info("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.log_error("Fatal error", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
