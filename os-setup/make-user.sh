#!/bin/bash

# make a user
sudo adduser elee
sudo usermod -a -G debian,adm,kmem,dialout,cdrom,floppy,audio,dip,video,plugdev,users,netdev,i2c,admin,spi,systemd-journal,weston-launch,xenomai elee
sudo service dbus reload
