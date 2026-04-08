#!/bin/bash

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

GREEN='\033[1;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# (permissions, user, group, destination)
# source is assumed to be "./destination"
install_thingy() {
  if [ -e $4 ]; then
    printf "${YELLOW}WARN: file '$4' already exists. Overwrite? (y/n) ${NC}"
    read -r YN
  else
    YN="Y"
  fi
  if [ "$YN" = "y" ]||[ "$YN" = "Y" ]; then
    install -D -m $1 -o $2 -g $3 "./$4" $4
    printf "${GREEN}OK: Installed '$4${NC}' \n\n"
  fi
}

install_thingy 644 root root "/etc/NetworkManager/NetworkManager.conf"
install_thingy 644 root root "/etc/systemd/network/10-create-bridge-br0.netdev"
install_thingy 644 root root "/etc/systemd/network/20-bind-ethernet-with-bridge-br0.network"
install_thingy 644 root root "/etc/systemd/network/30-config-bridge-br0.network"
install_thingy 644 root root "/etc/systemd/network/80-can.network"
install_thingy 600 root root "/etc/dnsmasq.d/00-bento-box.conf"
install_thingy 644 root root "/etc/systemd/system/bento-hostapd.service"
install_thingy 600 root root "/etc/hostapd/bento-box-AP.conf"


printf "${GREEN}set wifi region? (y/n)${NC}%s "
read -r YN
if [ "$YN" = "y" ]||[ "$YN" = "Y" ]; then
  RET=1
  while [ $RET != 0 ]; do
    printf "${GREEN}what region? (ISO/IEC 3166-1 alpha2, 2 char name)${NC}"
    read -r REG
    # We're running on raspi here, otherwise use `iw reg`
    raspi-config nonint do_wifi_country "${REG}"
    #sudo iw reg set "${REG}"
    RET=$?
  done
  sudo iw reg get | grep country
fi


PI_FW="/boot/firmware/config.txt"
if grep -q "bento robot" $PI_FW ; then
  printf "${YELLOW}WARN: Pi config, ${PI_FW}, already was modified. Skipping \n ${NC}"
else
  cat ./boot/firmware/config.txt >>"$PI_FW"
  printf "${GREEN}OK: Pi config, ${PI_FW}, modified. \n ${NC}"
fi

PI_BASHRC="$HOME/.bashrc"
if grep -q "bento robot" $PI_BASHRC ; then
  printf "${YELLOW}WARN: Pi bashrc, ${PI_BASHRC}, already was modified. Skipping \n ${NC}"
else
  cat ./bashrc.bash >>"$PI_BASHRC"
  printf "${GREEN}OK: Pi bashrc, ${PI_BASHRC}, modified. \n ${NC}"
fi


systemctl daemon-reload
# enable network configs
systemctl enable systemd-networkd
systemctl start systemd-networkd
printf "${GREEN}OK: enabled & started systemd-networkd \n ${NC}"
# enable DHCP & DNS server
systemctl enable dnsmasq &>/dev/null #STFU sysV
systemctl start dnsmasq
printf "${GREEN}OK: enabled & started dnsmasq \n ${NC}"
# set up wifi AP
systemctl unmask bento-hostapd.service
systemctl enable bento-hostapd.service &>/dev/null #STFU sysV
systemctl start bento-hostapd.service
printf "${GREEN}OK: enabled wifi AP \n ${NC}"
