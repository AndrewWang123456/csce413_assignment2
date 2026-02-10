#!/usr/bin/env python3
import socket
import argparse
import time


def scan_port(target, port, timeout=0.3):
    start_time = time.time()
    banner = ""

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)

        result = sock.connect_ex((target, port))

        elapsed = time.time() - start_time

        if result == 0:
            # Try banner grabbing
            try:
                sock.sendall(b"\r\n")
                banner = sock.recv(1024).decode(errors="ignore").strip()
            except Exception:
                banner = ""

            sock.close()
            return {
                "port": port,
                "state": "OPEN",
                "time": elapsed,
                "banner": banner
            }

        sock.close()
        return {
            "port": port,
            "state": "CLOSED",
            "time": elapsed,
            "banner": ""
        }

    except Exception:
        elapsed = time.time() - start_time
        return {
            "port": port,
            "state": "FILTERED",
            "time": elapsed,
            "banner": ""
        }


def parse_ports(port_range):
    try:
        start, end = port_range.split("-")
        return int(start), int(end)
    except ValueError:
        raise argparse.ArgumentTypeError("Port range must be in format start-end")


def main():
    parser = argparse.ArgumentParser(description="Custom TCP Port Scanner")
    parser.add_argument("--target", required=True, help="Target IP or hostname")
    parser.add_argument("--ports", required=True, help="Port range (e.g. 1-1000)")
    args = parser.parse_args()

    start_port, end_port = parse_ports(args.ports)

    print(f"[*] Scanning {args.target} ports {start_port}-{end_port}")
    print("-" * 60)

    open_ports = []

    for port in range(start_port, end_port + 1):
        result = scan_port(args.target, port)

        print(
            f"Port {result['port']:5} | "
            f"{result['state']:8} | "
            f"{result['time']:.3f}s | "
            f"{result['banner']}"
        )

        if result["state"] == "OPEN":
            open_ports.append(result)

    print("\n[+] Scan complete")
    print(f"[+] Open ports found: {len(open_ports)}")

    for p in open_ports:
        print(f"    Port {p['port']} OPEN — {p['banner']}")


if __name__ == "__main__":
    main()
