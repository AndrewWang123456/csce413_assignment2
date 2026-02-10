# SSH Honeypot

## Overview

This SSH honeypot simulates a legitimate OpenSSH server to detect and log unauthorized access attempts. It appears as a real SSH service but logs all authentication attempts without ever granting access.

## Purpose

- **Detect Attacks:** Log all connection attempts to identify reconnaissance activity
- **Gather Intelligence:** Collect usernames, passwords, and attack patterns
- **Distract Attackers:** Waste attacker time on a decoy system
- **Early Warning:** Alert security teams to potential threats

## How It Works

1. Honeypot listens on port 22 (standard SSH port)
2. Presents authentic SSH banner: `SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5`
3. Accepts connections and prompts for authentication
4. Logs all username/password attempts
5. Always rejects authentication (never grants access)
6. Keeps attackers engaged to learn their methods

## Files

- `honeypot.py` - Main SSH honeypot server
- `logger.py` - Log analysis and reporting tool
- `Dockerfile` - Container configuration
- `logs/` - Directory for log files (created automatically)
- `analysis.md` - Sample attack analysis
- `README.md` - This file

## Quick Start

### Running the Honeypot

```bash
# With Docker (recommended)
docker-compose up honeypot

# Local testing (requires Python 3.8+)
pip install paramiko
python honeypot.py
```

The honeypot will start on port 22 and log all activity.

### Testing the Honeypot

Simulate attacks to generate logs:

```bash
# Attack 1: Common credentials
ssh admin@localhost -p 2222
Password: admin

# Attack 2: Root access
ssh root@localhost -p 2222
Password: password123

# Attack 3: Generic testing
ssh test@localhost -p 2222
Password: test
```

All attempts will be rejected but logged.

### Viewing Logs

```bash
# View activity log
docker logs 2_network_honeypot

# Or check log files directly
cat logs/honeypot.log

# View authentication attempts (JSON)
cat logs/auth_attempts.json
```

### Analyzing Attacks

```bash
# Run log analysis
docker exec 2_network_honeypot python logger.py

# Or locally
python logger.py
```

Output shows:
- Total authentication attempts
- Most common usernames
- Most common passwords
- Unique attacker IP addresses
- Attack timeline

## Log Files

### honeypot.log
Human-readable activity log with timestamps:
```
2026-02-10 01:23:45 - INFO - 🔌 New connection from 172.17.0.1:54321
2026-02-10 01:23:47 - WARNING - 🔐 AUTH ATTEMPT from 172.17.0.1:54321 - Username: 'admin', Password: 'admin'
2026-02-10 01:23:51 - INFO - 👋 Connection closed: 172.17.0.1:54321
```

## Example Output

### Activity Log
```
[2026-02-10 12:34:56] - INFO - 🍯 SSH HONEYPOT STARTING
[2026-02-10 12:34:56] - INFO - 📡 Listening on port 22
[2026-02-10 12:34:56] - INFO - ✅ Honeypot is ready! Waiting for attackers...
[2026-02-10 12:35:12] - INFO - 🔌 New connection from 192.168.1.100:52341
[2026-02-10 12:35:15] - WARNING - 🔐 AUTH ATTEMPT from 192.168.1.100:52341 - Username: 'root', Password: 'password'
[2026-02-10 12:35:17] - WARNING - 🔐 AUTH ATTEMPT from 192.168.1.100:52341 - Username: 'admin', Password: 'admin123'
[2026-02-10 12:35:20] - INFO - 👋 Connection closed: 192.168.1.100:52341
```

### Best Practices

1. **Isolation:** Run in isolated network segment
2. **Monitoring:** Actively monitor for compromises
3. **Updates:** Keep Python and Paramiko updated
4. **Logs:** Protect logs from attackers
5. **Alert:** Set up alerts for suspicious activity

## Troubleshooting

**Port 22 already in use:**
```bash
# Check what's using it
sudo lsof -i :22

# Either stop the service or run honeypot on different port
```

**No logs appearing:**
```bash
# Check log directory permissions
ls -la logs/

# Verify honeypot is running
docker ps | grep honeypot
docker logs 2_network_honeypot
```

**Connection refused:**
```bash
# Check if honeypot is listening
netstat -tlnp | grep 22

# Verify firewall rules
sudo iptables -L | grep 22
```

**Paramiko errors:**
```bash
# Reinstall paramiko
pip uninstall paramiko
pip install paramiko
```


**Scalability:** Can handle hundreds of concurrent connections.

## Future Enhancements

- [ ] HTTP/FTP honeypots (multi-protocol)
- [ ] Interactive shell simulation (fake file system)
- [ ] Command logging for post-auth interaction
- [ ] Machine learning for attack classification
- [ ] Web dashboard for real-time monitoring
- [ ] Geographic IP mapping
- [ ] Automatic threat intel submission
- [ ] Integration with fail2ban