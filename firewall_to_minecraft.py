from scapy.all import *
import subprocess
from collections import defaultdict
from datetime import datetime, timedelta
from mcrcon import MCRcon
import time
import sys

# Minecraft RCON settings
RCON_PASSWORD = 'Subscribe2GnarCoding!'
RCON_PORT = 25575

# Scan tracking
scan_tracker = defaultdict(lambda: {"count": 0, "timestamp": None})
BLOCK_DURATION = timedelta(minutes=10)
SCAN_THRESHOLD = 0  # Scans to trigger block/zombie
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

def send_to_minecraft(ip, port, x, y, z):
    """Spawn zombie in Minecraft."""
    ip_parts = ip.split('.')
    masked_ip = f"{ip_parts[0]}.x.x.{ip_parts[3]}"
    custom_name = f"{masked_ip}:{port}"
    try:
        with MCRcon('localhost', RCON_PASSWORD, RCON_PORT) as mcr:
            command = f'summon zombie {x} {y} {z} {{CustomName:"\\"{custom_name}\\""}}'
            mcr.command(command)
            print(f"Spawned zombie for IP: {custom_name} at coordinates ({x}, {y}, {z})")
    except Exception as e:
        print(f"Error spawning zombie for IP {masked_ip}: {e}")

def handle_packet(packet, x, y, z):
    if TCP in packet and packet[TCP].flags == "S":  # SYN flag
        src_ip = packet[IP].src
        port = packet[TCP].dport
        current_time = datetime.now()

        # Print IP with .x.x for the middle 2 bytes
        ip_parts = src_ip.split('.')
        masked_ip = f"{ip_parts[0]}.x.x.{ip_parts[3]}"
        print(f"Scan detected on port {port} from {masked_ip}")

        # Update scan tracker
        if scan_tracker[src_ip]["timestamp"] and current_time - scan_tracker[src_ip]["timestamp"] > BLOCK_DURATION:
            scan_tracker[src_ip] = {"count": 0, "timestamp": None}

        scan_tracker[src_ip]["count"] += 1
        scan_tracker[src_ip]["timestamp"] = current_time

        # Check if threshold exceeded
        if scan_tracker[src_ip]["count"] > SCAN_THRESHOLD:
            print(f"IP {src_ip} exceeded scan limit, blocking and spawning zombie...")
            block_ip(src_ip)
            send_to_minecraft(src_ip, port, x, y, z)
            unblock_time = current_time + BLOCK_DURATION
            unblock_tasks.append({"ip": src_ip, "unblock_time": unblock_time})
            print(f"IP {masked_ip} will be unblocked at {unblock_time.strftime('%Y-%m-%d %H:%M:%S')}")

def unblock_expired_ips():
    """Unblock IPs whose duration has expired."""
    now = datetime.now()
    for task in list(unblock_tasks):
        if now >= task["unblock_time"]:
            unblock_ip(task["ip"])
            unblock_tasks.remove(task)

def main():
    if len(sys.argv) != 4:
        print("Usage: python firewall_to_minecraft.py <x> <y> <z>")
        sys.exit(1)

    x, y, z = sys.argv[1], sys.argv[2], sys.argv[3]

    print("Starting port scan detection...")
    while True:
        try:
            # Sniff for 5 seconds, then check unblocks
            sniff(filter="tcp", prn=lambda packet: handle_packet(packet, x, y, z), timeout=5)
            unblock_expired_ips()
        except Exception as e:
            print(f"Error in sniff loop: {e}")
            time.sleep(1)  # Brief pause before retrying

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopping...")