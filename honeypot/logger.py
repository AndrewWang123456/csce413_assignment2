"""Logging helpers and analysis for the honeypot."""
import json
from collections import Counter
from datetime import datetime


def analyze_auth_logs(logfile='/app/logs/auth_attempts.json'):
    """Analyze authentication attempts from honeypot"""
    
    print("\n" + "="*60)
    print("🔍 HONEYPOT LOG ANALYSIS")
    print("="*60 + "\n")
    
    try:
        attempts = []
        with open(logfile, 'r') as f:
            for line in f:
                if line.strip():
                    attempts.append(json.loads(line))
    except FileNotFoundError:
        print("❌ No auth log file found. No attacks recorded yet.")
        return
    except Exception as e:
        print(f"❌ Error reading logs: {e}")
        return
    
    if not attempts:
        print("ℹ️  No authentication attempts logged yet.")
        return
    
    print(f"📊 Total authentication attempts: {len(attempts)}\n")
    
    # Most common usernames
    usernames = Counter(a['username'] for a in attempts)
    print("👤 Top 10 Usernames Attempted:")
    for username, count in usernames.most_common(10):
        print(f"   {username:20s} - {count} attempts")
    print()
    
    # Most common passwords
    passwords = Counter(a['password'] for a in attempts)
    print("🔑 Top 10 Passwords Attempted:")
    for password, count in passwords.most_common(10):
        print(f"   {password:20s} - {count} attempts")
    print()
    
    # Unique IPs
    ips = Counter(a['client_ip'] for a in attempts)
    print(f"🌐 Unique IP Addresses: {len(ips)}")
    for ip, count in ips.most_common():
        print(f"   {ip:15s} - {count} attempts")
    print()
    
    # Time analysis
    if attempts:
        first = datetime.fromisoformat(attempts[0]['timestamp'])
        last = datetime.fromisoformat(attempts[-1]['timestamp'])
        duration = last - first
        print(f"⏰ Attack Timeline:")
        print(f"   First attempt: {first}")
        print(f"   Last attempt:  {last}")
        print(f"   Duration:      {duration}")
    
    print("\n" + "="*60 + "\n")


def create_logger():
    """Setup logging (already handled in honeypot.py)"""
    pass


if __name__ == "__main__":
    analyze_auth_logs()