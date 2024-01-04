#!/bin/bash

apt update

# Install minimum LXC requirements
apt install libc6 libpam-cgfs libcap-dev libapparmor-dev libselinux1-dev libseccomp-dev libgnutls30 liblua5.4-dev python3-dev uidmap

# Install LXC
apt install lxc lxc-templates lxctl
lxc-checkconfig
