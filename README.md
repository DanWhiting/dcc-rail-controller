# DCC Rail Controller
A project for controlling DCC model railway equipment via a web interface hosted on a Raspberry Pi Zero 2W.

The hardware setup consists of:
1. A simple track power driver PCB based on an LMD18200 3A, 55V H-Bridge.
2. An ESP32 dev kit, responsible for reliably sending DCC packets via the track power driver.
3. A Rasberry Pi Zero 2W, responsible for hosting the control web interface and sending packets to the ESP32.

Designed to conform to NMRA S-9.2 and S-9.2.1 standards.

Currently does not support extended decoder addresses.

The current approach assumes that synchronous communication is always good enough.
In the future, this could be extended to add async controllers and async dcc device classes.

# Status
Early Development - many features are being changed and added, there is no requirement for or expectation of stability.

# Quick Start
This quick start guide has only been tested with a Rasberry Pi Zero 2W running Raspberry Pi OS Lite (Debian Trixie).

## Pi Initial Setup
- Setup Raspberry OS Lite in headless mode connected to a local wifi network.
- System update:
```
sudo apt update
sudo apt upgrade
```

## Network Setup
Follow these steps to set up the pi with a local hotspot which will be the default wifi mode on boot.
Follow similar steps to add any other new private networks for internet access but ensure that they are not set to connect automatically.

1. Create a new wifi network config using `sudo nmtui`:
    - Name: PiRailHotspot
    - SSID: PiRailControl
    - Mode: Access Point
    - Security: WPA & WPA2 Personal, Password: YourPassword
    - IPv4 configuration: Manual (manual is chosen to prevent NetworkManager from launching its own dnsmasq service)
        - Add an address: 192.168.4.1/24
    - Enable "Automatically connect"
2. Edit the existing config for the original wifi network to remove the autoconnect option and exit the config tool. This should ensure that the hotspot is connected on boot by default.

### Switching Networks
- Switch between networks using `sudo nmcli con up NetworkName`
- For now, leave the external wifi connection active.

### Remote SSH to the Pi
- When the Pi is on the local wifi network, it should be accessible via its hostname e.g. pi-rail.
- When the Pi is acting as the access point (hotspot), it should be accessible via its static ip that we defined above.

## Enabling Bluetooth
I went through several steps to get bluetooth working, I will list them all here but i'm not certain which are the minimum actually required.

1. `sudo apt install libdbus-1-dev libbluetooth-dev bluez bluetooth`

2. Adding the user to the bluetooth group: `sudo usermod -aG bluetooth YourUserName`

3. For some reason bluetooth was soft-blocked on my system, see output of `rfkill list`.
This could be as a result of unset localisation options which can be set in the Pi config `sudo raspi-config`.
I ensured these were set correctly and then manually ran `sudo rfkill unblock bluetooth` to clear the block.
After restarting the system, the bluetooth service started correctly.

## Web Server Setup
1. Install git `sudo apt install git`
2. Clone the project repo `git clone 'https://github.com/DanWhiting/dcc-rail-controller'`
3. Install uv `curl -LsSf https://astral.sh/uv/install.sh | sh`
4. Restart the remote shell (to update the path) and cd into the project repo.
5. Run `uv sync`
6. Create a new service to run the server on boot `sudo nano /etc/systemd/system/pi-rail.service`
```
[Unit]
Description=Train Control Web Server
After=network-online.target NetworkManager.service
Wants=network-online.target
StartLimitIntervalSec=300
StartLimitBurst=3

[Service]
ExecStartPre=/bin/sleep 5
ExecStart=/home/YourUserName/.local/bin/uv run /home/YourUserName/dcc-rail-controller/server.py
WorkingDirectory=/home/YourUserName/dcc-rail-controller
StandardOutput=inherit
StandardError=inherit
User=YourUserName
# Currently Restart=no but will change to always later when stable
Restart=no 
RestartSec=10

[Install]
WantedBy=multi-user.target
```
4. Enable and start the service
```
sudo systemctl enable pi-rail.service
sudo systemctl start pi-rail.service
```

### Permenantly Redirect Port 80 to Port 5000
Because we are running our Flask server on port 5000, we can redirect traffic from port 80 to make access simple.
```
sudo systemctl enable nftables
sudo nft add table ip nat
sudo nft add chain ip nat prerouting { type nat hook prerouting priority 0 \; }
sudo nft add rule ip nat prerouting tcp dport 80 redirect to :5000
sudo sh -c "nft list ruleset > /etc/nftables.conf"
sudo systemctl restart nftables
```

### Install and Configure DNS Masking
Normally, when a device (like a phone) connects to Wi-Fi, it asks a DNS server, "Where is google.com?" and the server gives the real internet address.

For this project, we want the Pi to lie. By using the "wildcard" rule (address=/#/192.168.4.1), we tell the Pi that no matter what website the phone asks for—be it Google, Apple, or a hidden background connectivity check—the answer is always 192.168.4.1 (the Pi itself).

When the phone tries to reach the "Internet" to verify the connection, it hits our local web server instead. This "fake" response is what triggers the smartphone to automatically pop up the "Sign in to network" screen.

>Note: For dnsmasq to work correctly, the Wi-Fi connection must be set to Manual mode in NetworkManager. If it is set to "Shared" mode, NetworkManager will try to run its own hidden version of dnsmasq, causing a conflict and preventing yours from starting.

1. Install dnsmasq `sudo apt install dnsmasq`
2. Enable the service `sudo systemctl enable dnsmasq`
3. Add the following lines to `sudo nano /etc/dnsmasq.conf`:
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
no-resolv
```
4. Restart the service `sudo systemctl restart dnsmasq`

### Testing
- Switch over to the hotspot network `sudo nmcli con up PiRailHotspot`
- Connect to the hotspot from a mobile device.
- If everything is working correctly, you should automatically be redirected to the controller page.

## ToDo
- Consider adding nginx as a reverse proxy to simplify connection and improve serving performance