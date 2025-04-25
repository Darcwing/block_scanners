# See scans with tcp dump
```bash
tcpdump -i eth0 'tcp[tcpflags] & tcp-syn != 0'
```

# Update package lists
```bash
sudo apt update && sudo apt upgrade
```
