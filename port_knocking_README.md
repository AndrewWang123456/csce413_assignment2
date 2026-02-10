# Port Knocking Implementation

## Overview

This port knocking system protects SSH access (port 2222) by hiding it behind a firewall until clients perform a specific knock sequence.

## How It Works

1. SSH port 2222 is blocked by default using iptables
2. Server listens on three knock ports: 1234, 5678, 9012
3. Client must connect to these ports in the correct order within 10 seconds
4. After successful knock, firewall opens port 2222 for that client's IP address
5. Client can then SSH to port 2222

## Knock Sequence

```
Port 1234 → Port 5678 → Port 9012
```

**Timing:** Must complete sequence within 10 seconds

## Files

- `knock_server.py` - Server that listens for knocks and manages firewall
- `knock_client.py` - Client to perform knock sequence
- `Dockerfile` - Container configuration
- `README.md` - This file

## Usage

### Running the Server

```bash
# Local testing
python knock_server.py

# With Docker
docker-compose up port_knocking
```

The server will:
- Listen on ports 1234, 5678, 9012
- Block port 2222 by default
- Log all knock attempts
- Open port 2222 for correct sequences

### Using the Client

```bash
# Perform knock sequence
python knock_client.py --target localhost --sequence 1234,5678,9012

# Perform knock and test connection
python knock_client.py --target localhost --sequence 1234,5678,9012 --check

# Knock a remote server
python knock_client.py --target 192.168.1.100 --sequence 1234,5678,9012
```

### Options

**Server:**
- `--sequence` - Comma-separated knock ports (default: 1234,5678,9012)
- `--protected-port` - Port to protect (default: 2222)
- `--window` - Seconds to complete sequence (default: 10)

**Client:**
- `--target` - Target hostname or IP (required)
- `--sequence` - Knock sequence (default: 1234,5678,9012)
- `--delay` - Delay between knocks in seconds (default: 0.3)
- `--check` - Test connection to protected port after knocking

## Example Workflow

```bash
# Terminal 1: Start the server
python knock_server.py

# Output:
# [2026-02-10 12:00:00] - INFO - 🔒 Initializing firewall rules...
# [2026-02-10 12:00:00] - INFO - 👂 Listening on knock port 1234
# [2026-02-10 12:00:00] - INFO - 👂 Listening on knock port 5678
# [2026-02-10 12:00:00] - INFO - 👂 Listening on knock port 9012
# [2026-02-10 12:00:00] - INFO - 🚀 Port knocking server is ready!

# Terminal 2: Perform the knock
python knock_client.py --target localhost --sequence 1234,5678,9012 --check

# Output:
# 🚪 Starting knock sequence on localhost
# [1/3] 🔨 Knocking on localhost:1234... ✅
# [2/3] 🔨 Knocking on localhost:5678... ✅
# [3/3] 🔨 Knocking on localhost:9012... ✅
# ✅ Knock sequence complete!
# 🔍 Checking if protected port 2222 is open...
# ✅ Successfully connected to port 2222!

# Terminal 3: Now you can SSH
ssh user@localhost -p 2222
```

## Security Considerations

### Strengths
- ✅ Hides SSH from port scanners
- ✅ Prevents automated brute-force attacks
- ✅ Adds layer before authentication
- ✅ Lightweight and simple

### Limitations
- ⚠️ Security through obscurity (not cryptographic)
- ⚠️ Knock sequence visible to network sniffers
- ⚠️ Vulnerable to replay attacks
- ⚠️ Not a replacement for strong authentication

### Best Practices
1. **Keep sequence secret** - Don't share publicly
2. **Change sequence periodically** - Rotate every few months
3. **Use with strong auth** - Still require SSH keys or MFA
4. **Monitor logs** - Watch for failed knock attempts
5. **Combine with VPN** - For additional security

## Troubleshooting

**Port already in use:**
```bash
# Check what's using the port
lsof -i :1234

# Kill the process or change knock sequence
```

**Firewall rules not working:**
```bash
# Check current rules
sudo iptables -L -n -v

# Manually test rule
sudo iptables -A INPUT -p tcp --dport 2222 -j DROP

# Clear all rules (use with caution)
sudo iptables -F
```

**Knock not detected:**
- Make sure server is running
- Check you're using correct IP address
- Verify ports are not blocked by other firewalls
- Try increasing delay between knocks

**Permission denied:**
```bash
# Run with sudo (needed for iptables)
sudo python knock_server.py
```

## How Port Knocking Compares

| Method | Security | Usability | Complexity |
|--------|----------|-----------|------------|
| Port Knocking | Medium | High | Low |
| VPN | High | Medium | Medium |
| IP Whitelist | Low | Low | Low |
| SSH Keys Only | High | High | Low |

**Recommendation:** Use port knocking + SSH keys + fail2ban for best results.

## Implementation Details

### Server Architecture
- Multi-threaded socket listeners on each knock port
- State tracking per IP address
- Timeout enforcement (10 second window)
- Automatic sequence reset on errors

### Client Flow
1. Connect to port 1234 (close immediately)
2. Wait 0.3 seconds
3. Connect to port 5678 (close immediately)
4. Wait 0.3 seconds
5. Connect to port 9012 (close immediately)
6. Port 2222 now accessible

### Firewall Management
```python
# Block port by default
iptables -A INPUT -p tcp --dport 2222 -j DROP

# Open for specific IP after correct knock
iptables -I INPUT 1 -p tcp --dport 2222 -s 192.168.1.100 -j ACCEPT
```

