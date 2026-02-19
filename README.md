# DCC-rail-controller
A collection of codes for controlling DCC model railway equipment.

Designed to conform to NMRA S-9.2 and S-9.2.1 standards.

Currently does not support extended decoder addresses.

The current approach assumes that synchronous communication is always good enough.
In the future, this could be extended to add async controllers and async dcc device classes.

# Quick Start

## Pi Initial Setup
- Setup Raspberry OS Lite in headless mode connected to your wifi network
- System update

## Network Setup
Follow these steps to set up the pi with a local hotspot which will be the default wifi mode on boot.
Follow similar steps to add any new private networks for internet access.

- Create a new network config using `sudo nmtui`:
    - Name: PiRailHotspot
    - SSID: PiRailControl
    - Mode: Access Point
    - Security: WPA & WPA2 Personal, Password: YourPassword
    - IPv4 configuration: Manual
        - Add an address: 192.168.4.1/24
    - Enable "Automatically connect"
- Edit the existing config for the original wifi network to remove the autoconnect option and exit the config tool.

- Switch over to the hotspot network `sudo nmcli con up PiRailHotspot`

### Switching Networks
- Switch between networks using `sudo nmcli con up <Network Name>` (supports tab completion)

### Remote SSH to the Pi
- When the Pi is on the local wifi network, it should be accessible via its hostname e.g. pi-rail
- When the Pi is acting as the access point, it should be accessible via its static ip defined above.

## Web Server Setup
- Install git `sudo apt install git`
- Clone the project repo `git clone 'https://github.com/DanWhiting/dcc-rail-controller`
- Install uv `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Restart the remote shell and cd into the project repo.
- Run `uv sync`


- Create `sudo nano /etc/systemd/system/pi-rail.service`
```
[Unit]
Description=Train Control Web Server
After=network.target

[Service]
ExecStartPre=/bin/sleep 5
ExecStart=/home/YourUserName/.local/bin/uv run /home/YourUserName/dcc-rail-controller/server.py
WorkingDirectory=/home/YourUserName/dcc-rail-controller
StandardOutput=inherit
StandardError=inherit
Restart=always
User=YourUserName

[Install]
WantedBy=multi-user.target
```

`sudo systemctl enable pi-rail.service`
`sudo systemctl start pi-rail.service`


### Permenantly redirect port 80 to port 5000
```
sudo systemctl enable nftables
sudo nft add table ip nat
sudo nft add chain ip nat prerouting { type nat hook prerouting priority 0 \; }
sudo nft add rule ip nat prerouting tcp dport 80 redirect to :5000
sudo sh -c "nft list ruleset > /etc/nftables.conf"
sudo systemctl restart nftables
```

### Install and configure dnsmasq to setup the capture/login prompt
```
sudo apt install dnsmasq
sudo nano /etc/dnsmasq.conf
```

Add the following lines:
```
# The "Liar" DNS rule
address=/#/192.168.4.1

# DHCP Server settings
# This hands out IPs from .50 to .150
dhcp-range=192.168.4.50,192.168.4.150,12h

# Tell the client that the Pi is the Gateway and the DNS server
dhcp-option=option:router,192.168.4.1
dhcp-option=option:dns-server,192.168.4.1

interface=wlan0
bind-dynamic
```

`sudo systemctl restart dnsmasq`

## ToDo
- Consider adding nginx as a reverse proxy to simplify connection and improve serving performance