#! /bin/sh
#
# cp-nm-config.sh
#
# Copy NetWork Manager config file template for mounted Worker image
# MARK: Use default mount path for Arch Linux

sudo rm -rf /run/media/steve/rootfs/etc/NetworkManager/system-connections/*
sudo cp ./worker_netmn_config /run/media/steve/rootfs/etc/NetworkManager/system-connections/ethernet_connection
