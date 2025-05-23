from scapy.all import *
import subprocess
from collections import defaultdict
from datetime import datetime, timedelta
import time
import sys

# Scan tracking
scan_tracker = defaultdict(lambda: {"count": 0, "timestamp": None})
BLOCK_DURATION = timedelta(minutes=120) # unblock scanner's IP after {BLOCK_DURATION} / 120 minutes
SCAN_THRESHOLD = 50  # Scans to trigger block
unblock_tasks = []

def is_ip_blocked(ip):
    """Check if IP is already blocked in iptables."""
    result = subprocess.run(["iptables", "-L", "-n"], stdout=subprocess.PIPE, text=True)
    return ip in result.stdout

def block_ip(ip):
    """Block IP with iptables."""
    if is_ip_blocked(ip):
        print(f"IP {ip} already blocked.")
        return
    print(f"Blocking IP: {ip}")
    try:
        subprocess.run(["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error blocking IP {ip}: {e}")

def unblock_ip(ip):
    """Unblock IP from iptables."""
    print(f"Unblocking IP: {ip}")
    try:
        subprocess.run(["iptables", "-D", "INPUT", "-s", ip, "-j", "DROP"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error unblocking IP {ip}: {e}")

def handle_packet(packet, SCAN_THRESHOLD, BLOCK_DURATION):
    if TCP in packet and packet[TCP].flags == "S":  # SYN flag
        src_ip = packet[IP].src
        port = packet[TCP].dport
        current_time = datetime.now()

        print(f"Scan detected on port {port} from {src_ip}")

        # Update scan tracker
        if scan_tracker[src_ip]["timestamp"] and current_time - scan_tracker[src_ip]["timestamp"] > BLOCK_DURATION:
            scan_tracker[src_ip] = {"count": 0, "timestamp": None}

        scan_tracker[src_ip]["count"] += 1
        scan_tracker[src_ip]["timestamp"] = current_time

        # Check if threshold exceeded
        if scan_tracker[src_ip]["count"] > SCAN_THRESHOLD:
            print(f"IP {src_ip} exceeded scan limit, blocking...")
            block_ip(src_ip)
            unblock_time = current_time + BLOCK_DURATION
            unblock_tasks.append({"ip": src_ip, "unblock_time": unblock_time})
            print(f"IP {src_ip} will be unblocked at {unblock_time.strftime('%Y-%m-%d %H:%M:%S')}")

def unblock_expired_ips():
    """Unblock IPs whose duration has expired."""
    now = datetime.now()
    for task in list(unblock_tasks):
        if now >= task["unblock_time"]:
            unblock_ip(task["ip"])
            unblock_tasks.remove(task)

def main():
    if len(sys.argv) != 4:
        print("Usage: python block_scanners.py \{Threshold\} \{BLOCK_DURATION\}")
        sys.exit(1)

    SCAN_THRESHOLD, BLOCK_DURATION = sys.argv[1], sys.argv[2]

    print("Starting port scan detection...")
    while True:
        try:
            # Sniff for 5 seconds, then check unblocks
            sniff(filter="tcp", prn=lambda packet: handle_packet(packet, SCAN_THRESHOLD, BLOCK_DURATION), timeout=5)
            unblock_expired_ips()
        except Exception as e:
            print(f"Error in sniff loop: {e}")
            time.sleep(1)  # Brief pause before retrying

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopping...")
