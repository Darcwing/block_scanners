# See scans with tcp dump
```bash
tcpdump -i eth0 'tcp[tcpflags] & tcp-syn != 0'
```

# Update package lists
```bash
sudo apt update && sudo apt upgrade
```

# Install Java 21
```bash
sudo apt install openjdk-21-jdk
java --version
```

# Download the Minecraft server
```bash
mkdir ~/minecraft
cd ~/minecraft
wget https://piston-data.mojang.com/v1/objects/e6ec2f64e6080b9b5d9b471b291c33cc7f509733/server.jar
java -Xmx1024M -jar server.jar nogui
```

# Setup server
```bash
nano eula.txt
# Set eula=true
```

# Configure RCON
Edit server.properties:
```bash
enable-rcon=true
rcon.password=Subscribe2GnarCoding!
rcon.port=25575
server-ip=
```

# Start the Server
```bash
java -Xmx2G -jar spigot-[version].jar nogui
```