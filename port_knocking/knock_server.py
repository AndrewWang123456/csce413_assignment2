#!/usr/bin/env python3
"""Starter template for the port knocking server."""

import argparse
import logging
import socket
import time
import subprocess
from datetime import datetime

DEFAULT_KNOCK_SEQUENCE = [1234, 5678, 9012]
DEFAULT_PROTECTED_PORT = 2222
DEFAULT_SEQUENCE_WINDOW = 10.0


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )


def open_protected_port(protected_port, client_ip):
    """Open the protected port using firewall rules."""
    logger = logging.getLogger("KnockServer")
    try:
        # Add iptables rule to allow this IP to access the protected port
        subprocess.run([
            "iptables", "-I", "INPUT", "1",
            "-p", "tcp",
            "--dport", str(protected_port),
            "-s", client_ip,
            "-j", "ACCEPT"
        ], check=True)
        logger.info(f"✅ Opened port {protected_port} for {client_ip}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to open port: {e}")
    except FileNotFoundError:
        logger.warning("iptables not found - running in demo mode (no actual firewall changes)")


def close_protected_port(protected_port):
    """Close the protected port using firewall rules."""
    logger = logging.getLogger("KnockServer")
    try:
        # Block all traffic to protected port by default
        subprocess.run([
            "iptables", "-A", "INPUT",
            "-p", "tcp",
            "--dport", str(protected_port),
            "-j", "DROP"
        ], check=True)
        logger.info(f"🔒 Closed port {protected_port} (default deny)")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to close port: {e}")
    except FileNotFoundError:
        logger.warning("iptables not found - running in demo mode")


def listen_for_knocks(sequence, window_seconds, protected_port):
    """Listen for knock sequence and open the protected port."""
    logger = logging.getLogger("KnockServer")
    logger.info("Listening for knocks: %s", sequence)
    logger.info("Protected port: %s", protected_port)
    logger.info(f"Sequence window: {window_seconds} seconds")

    # Track knock attempts: {ip_address: {'ports': [port1, port2], 'start_time': timestamp}}
    knock_attempts = {}

    # Create TCP listeners for each knock port
    sockets = []
    for port in sequence:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('0.0.0.0', port))
            sock.listen(5)
            sock.settimeout(0.1)  # Non-blocking with short timeout
            sockets.append((port, sock))
            logger.info(f"👂 Listening on knock port {port}")
        except Exception as e:
            logger.error(f"Failed to bind to port {port}: {e}")
            continue

    logger.info("🚀 Port knocking server is ready!")

    while True:
        for knock_port, sock in sockets:
            try:
                conn, addr = sock.accept()
                client_ip = addr[0]
                logger.info(f"🔔 Knock from {client_ip} on port {knock_port}")
                conn.close()

                current_time = time.time()

                # Initialize tracking for this IP if not exists
                if client_ip not in knock_attempts:
                    knock_attempts[client_ip] = {
                        'ports': [],
                        'start_time': current_time
                    }

                # Check if sequence window expired
                elapsed = current_time - knock_attempts[client_ip]['start_time']
                if elapsed > window_seconds:
                    logger.warning(f"⏰ Timeout for {client_ip} ({elapsed:.1f}s > {window_seconds}s) - Resetting")
                    knock_attempts[client_ip] = {
                        'ports': [knock_port],
                        'start_time': current_time
                    }
                else:
                    # Add this knock to the sequence
                    knock_attempts[client_ip]['ports'].append(knock_port)

                # Get current progress
                current_sequence = knock_attempts[client_ip]['ports']
                logger.info(f"📊 {client_ip} sequence: {current_sequence}")

                # Check if sequence is complete and correct
                if len(current_sequence) == len(sequence):
                    if current_sequence == sequence:
                        logger.info(f"✅ CORRECT SEQUENCE from {client_ip}!")
                        logger.info(f"🔓 Opening port {protected_port} for {client_ip}")
                        open_protected_port(protected_port, client_ip)
                        del knock_attempts[client_ip]  # Clear successful attempt
                    else:
                        logger.warning(f"❌ INCORRECT SEQUENCE from {client_ip}: {current_sequence}")
                        logger.info(f"Expected: {sequence}")
                        del knock_attempts[client_ip]  # Reset failed attempt

            except socket.timeout:
                continue  # No connection, keep listening
            except Exception as e:
                logger.error(f"Error: {e}")

        # Clean up old attempts
        current_time = time.time()
        expired_ips = [
            ip for ip, data in knock_attempts.items()
            if current_time - data['start_time'] > window_seconds
        ]
        for ip in expired_ips:
            logger.info(f"🧹 Cleaning up expired attempt from {ip}")
            del knock_attempts[ip]

        time.sleep(0.01)  # Small sleep to prevent CPU spinning


def parse_args():
    parser = argparse.ArgumentParser(description="Port knocking server starter")
    parser.add_argument(
        "--sequence",
        default=",".join(str(port) for port in DEFAULT_KNOCK_SEQUENCE),
        help="Comma-separated knock ports",
    )
    parser.add_argument(
        "--protected-port",
        type=int,
        default=DEFAULT_PROTECTED_PORT,
        help="Protected service port",
    )
    parser.add_argument(
        "--window",
        type=float,
        default=DEFAULT_SEQUENCE_WINDOW,
        help="Seconds allowed to complete the sequence",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    setup_logging()

    try:
        sequence = [int(port) for port in args.sequence.split(",")]
    except ValueError:
        raise SystemExit("Invalid sequence. Use comma-separated integers.")

    # Close the protected port by default
    logger = logging.getLogger("KnockServer")
    logger.info("🔒 Initializing firewall rules...")
    close_protected_port(args.protected_port)

    listen_for_knocks(sequence, args.window, args.protected_port)


if __name__ == "__main__":
    main()