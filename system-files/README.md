# Bento-Box system files
*This directory contains the configuration files and setup guide for Bento-Box's system setup.*  
Versioning these files helps keep track of changes, and turns worst-case scenarios (for instance a dead SD card) from disqualifying events into something that can be solved in a few minutes.

> We recommend using whatever OS works best for your hardware,  
> but prefer Debian as it is designed for servers and therefore very stable and lightweight.  
> Docker gets around OS restrictions (such as ROS only distributing for ubuntu).

## Install configuration
Files are laid out in the same way that they would be in the system.
> e.g. `etc/NetworkManager/xyz` → `/etc/NetworkManager/xyz`

`./setup.sh` provided in this directory does the exact same as the manual steps.

⚠️ **reboot to make changes take effect**, once you are done ofc


## Install software

> ℹ️ **internet required!**  
> you can test your connection using `ping google.com`

```shell
# Install software (everything after 'git' is optional)
sudo apt update
sudo apt install docker.io docker-compose dnsmasq hostapd ifupdown git gh lazygit can-utils i2c-tools libcamera-tools btop stress iperf3 tree lolcat -y  # presume that systemd-networkd is preinstalled, like on raspi
# say yes to auto-start iperf3

# Set up user docker permissions
sudo usermod -aG docker $USER
```
```shell
# Set up this Repo, Build image, and start container
cd ~/
git clone https://github.com/Bento-Robotics/Bento-Box.git

# set up host configs
cd ~/Bento-Box/system-files/
sudo ./setup.sh

# ℹ️ you will lose connection,
# just wait for the reboot and WiFi coming up.
sudo reboot
```
> Log back in to robot, now WiFi and Ethernet work as "hotspots"
```shell
# Set up container (needs Internet. I suggest USB tethering with a phone)
cd ~/Bento-Box/container/
sudo docker compose up -d
cd ~/
```
```shell
# (Optional) Set up git
gh auth login
# follow instructions and log into github
git config --global user.email "bento.robotics@gmail.com"
git config --global user.name "Bento-Box"
```


## Manual install

### CAN - systemd-networkd
> /etc/systemd/network/80-can.network
```shell
sudo systemctl enable systemd-networkd
sudo systemctl start systemd-networkd
```

### DNS & DHCP - dnsmasq
> /etc/dnsmasq.d/00-bento-box.conf
```shell
sudo chmod 600 /etc/dnsmasq.d/00-bento-box.conf
sudo chown root /etc/dnsmasq.d/00-bento-box.conf
sudo chgrp root /etc/dnsmasq.d/00-bento-box.conf

sudo systemctl enable dnsmasq.service  # ignore perl's complaining
sudo systemctl start dnsmasq.service
```

### WiFi & Ethernet - netplan
> /etc/netplan/00-bento-box.yaml
```shell
sudo chmod 600 /etc/netplan/00-bento-box.yaml
sudo chown root /etc/netplan/00-bento-box.yaml
sudo chgrp root /etc/netplan/00-bento-box.yaml

sudo raspi-config nonint do_wifi_country DE  # or whatever county you are in
sudo netplan apply
```

### Raspi Config
> /boot/firmware/config.txt

⚠️ **DON'T overwrite it!!**, only append what we need like so:
```shell
echo ./boot/firmware/config.txt >>/boot/firmware/config.txt
```
