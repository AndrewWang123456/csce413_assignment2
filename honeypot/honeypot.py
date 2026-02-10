#!/usr/bin/env python3
"""SSH Honeypot - Logs unauthorized access attempts"""
import logging
import os
import socket
import threading
import paramiko
import json
from datetime import datetime

LOG_PATH = "/app/logs/honeypot.log"
AUTH_LOG_PATH = "/app/logs/auth_attempts.json"


def setup_logging():
    """Setup logging to file and console"""
    os.makedirs("/app/logs", exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(LOG_PATH),
            logging.StreamHandler()
        ],
    )


class SSHHoneypot(paramiko.ServerInterface):
    """SSH Server Interface for Honeypot"""
    
    def __init__(self, client_ip, client_port):
        self.client_ip = client_ip
        self.client_port = client_port
        self.event = threading.Event()
        self.logger = logging.getLogger("SSHHoneypot")
        
    def check_auth_password(self, username, password):
        """Log all password authentication attempts"""
        self.logger.warning(
            f"🔐 AUTH ATTEMPT from {self.client_ip}:{self.client_port} - "
            f"Username: '{username}', Password: '{password}'"
        )
        
        # Save to JSON log for analysis
        auth_data = {
            'timestamp': datetime.now().isoformat(),
            'client_ip': self.client_ip,
            'client_port': self.client_port,
            'username': username,
            'password': password,
            'auth_type': 'password',
            'result': 'denied'
        }
        
        try:
            with open(AUTH_LOG_PATH, 'a') as f:
                f.write(json.dumps(auth_data) + '\n')
        except Exception as e:
            self.logger.error(f"Failed to write auth log: {e}")
        
        # Always reject authentication (it's a honeypot!)
        return paramiko.AUTH_FAILED
    
    def check_auth_publickey(self, username, key):
        """Log public key authentication attempts"""
        self.logger.warning(
            f"🔑 PUBKEY AUTH from {self.client_ip}:{self.client_port} - "
            f"Username: '{username}', Key type: {key.get_name()}"
        )
        return paramiko.AUTH_FAILED
    
    def get_allowed_auths(self, username):
        """Tell client we support password auth"""
        return 'password,publickey'
    
    def check_channel_request(self, kind, chanid):
        """Allow channel requests to keep connection alive"""
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    
    def check_channel_shell_request(self, channel):
        """Log shell requests"""
        self.logger.info(f"🖥️  Shell requested by {self.client_ip}")
        return False
    
    def check_channel_exec_request(self, channel, command):
        """Log command execution attempts"""
        self.logger.warning(
            f"⚠️  COMMAND EXEC from {self.client_ip}: {command.decode('utf-8', errors='ignore')}"
        )
        return False


def generate_or_load_host_key():
    """Generate or load RSA host key"""
    key_path = '/app/logs/ssh_host_rsa_key'
    
    if os.path.exists(key_path):
        return paramiko.RSAKey.from_private_key_file(key_path)
    else:
        key = paramiko.RSAKey.generate(2048)
        key.write_private_key_file(key_path)
        return key


def handle_client(client_socket, client_addr):
    """Handle individual SSH client connection"""
    logger = logging.getLogger("SSHHoneypot")
    client_ip = client_addr[0]
    client_port = client_addr[1]
    
    logger.info(f"🔌 New connection from {client_ip}:{client_port}")
    
    try:
        # Setup SSH transport
        transport = paramiko.Transport(client_socket)
        transport.local_version = "SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5"  # Fake Ubuntu SSH banner
        
        # Add server key
        host_key = generate_or_load_host_key()
        transport.add_server_key(host_key)
        
        # Start SSH server
        server = SSHHoneypot(client_ip, client_port)
        transport.start_server(server=server)
        
        # Wait for authentication
        channel = transport.accept(30)  # 30 second timeout
        
        if channel is None:
            logger.info(f"❌ {client_ip} - No channel opened (likely failed auth)")
        else:
            logger.info(f"⚠️  {client_ip} - Channel opened (shouldn't happen in honeypot!)")
            channel.close()
        
        # Keep connection alive briefly to log more attempts
        server.event.wait(10)
        
    except paramiko.SSHException as e:
        logger.info(f"🚫 SSH error from {client_ip}: {e}")
    except Exception as e:
        logger.error(f"💥 Error handling {client_ip}: {e}")
    finally:
        try:
            transport.close()
        except:
            pass
        logger.info(f"👋 Connection closed: {client_ip}:{client_port}")


def run_honeypot(port=22):
    """Main honeypot server loop"""
    logger = logging.getLogger("Honeypot")
    
    logger.info("=" * 60)
    logger.info("🍯 SSH HONEYPOT STARTING")
    logger.info("=" * 60)
    logger.info(f"📡 Listening on port {port}")
    logger.info(f"📝 Logs: {LOG_PATH}")
    logger.info(f"📊 Auth logs: {AUTH_LOG_PATH}")
    logger.info("=" * 60)
    
    # Create server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(100)
    
    logger.info("✅ Honeypot is ready! Waiting for attackers...")
    
    # Accept connections
    while True:
        try:
            client_socket, client_addr = server_socket.accept()
            
            # Handle each connection in a separate thread
            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, client_addr),
                daemon=True
            )
            client_thread.start()
            
        except KeyboardInterrupt:
            logger.info("\n🛑 Shutting down honeypot...")
            break
        except Exception as e:
            logger.error(f"Error accepting connection: {e}")


if __name__ == "__main__":
    setup_logging()
    run_honeypot()