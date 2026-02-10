#!/usr/bin/env python3
"""Starter template for the port knocking client."""

import argparse
import socket
import time

DEFAULT_KNOCK_SEQUENCE = [1234, 5678, 9012]
DEFAULT_PROTECTED_PORT = 2222
DEFAULT_DELAY = 0.3


def send_knock(target, port, delay):
    """Send a single knock to the target port."""
    print(f"🔨 Knocking on {target}:{port}...", end=" ")
    
    # TCP knock - just connect and disconnect
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.0)
        sock.connect((target, port))
        sock.close()
        print("✅")
    except socket.timeout:
        print("⏰ (timeout - but knock sent)")
    except ConnectionRefusedError:
        print("✅ (connection refused - but knock registered)")
    except OSError as e:
        print(f"⚠️  ({e})")
    
    time.sleep(delay)


def perform_knock_sequence(target, sequence, delay):
    """Send the full knock sequence."""
    print(f"\n🚪 Starting knock sequence on {target}")
    print(f"📋 Sequence: {sequence}")
    print(f"⏱️  Delay between knocks: {delay}s\n")
    
    for i, port in enumerate(sequence, 1):
        print(f"[{i}/{len(sequence)}] ", end="")
        send_knock(target, port, delay)
    
    print(f"\n✅ Knock sequence complete!")
    print(f"🔓 Port {DEFAULT_PROTECTED_PORT} should now be accessible\n")


def check_protected_port(target, protected_port):
    """Try connecting to the protected port after knocking."""
    print(f"🔍 Checking if protected port {protected_port} is open...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2.0)
        sock.connect((target, protected_port))
        sock.close()
        print(f"✅ Successfully connected to port {protected_port}!")
        print(f"🎉 Port knocking worked!\n")
        return True
    except socket.timeout:
        print(f"❌ Connection timeout on port {protected_port}")
        print(f"⚠️  Port may still be closed\n")
        return False
    except ConnectionRefusedError:
        print(f"❌ Connection refused on port {protected_port}")
        print(f"⚠️  Knock sequence may have been incorrect\n")
        return False
    except OSError as e:
        print(f"❌ Could not connect to port {protected_port}: {e}\n")
        return False


def parse_args():
    parser = argparse.ArgumentParser(description="Port knocking client starter")
    parser.add_argument("--target", required=True, help="Target host or IP")
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
        "--delay",
        type=float,
        default=DEFAULT_DELAY,
        help="Delay between knocks in seconds",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Attempt connection to protected port after knocking",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        sequence = [int(port) for port in args.sequence.split(",")]
    except ValueError:
        raise SystemExit("Invalid sequence. Use comma-separated integers.")

    perform_knock_sequence(args.target, sequence, args.delay)

    if args.check:
        check_protected_port(args.target, args.protected_port)


if __name__ == "__main__":
    main()