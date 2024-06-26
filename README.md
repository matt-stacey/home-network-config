# home-network-config
Salt and LXC setup for home network

## LXC Preparation

### LXC Containers - Getting Started
https://linuxcontainers.org/lxc/getting-started/

### Linux Containers
https://wiki.archlinux.org/title/Linux_Containers

### Requirements
- glibc, musl libc, uclib or bionic
- Linux kernel >= 3.12
- libpam-cgfs
- shadow including newuidmap and newgidmap
- libcap (to allow for capability drops)
- libapparmor (to set a different apparmor profile for the container)
- libselinux (to set a different selinux context for the container)
- libseccomp (to set a seccomp policy for the container)
- libgnutls (for various checksumming)
- liblua (for the LUA binding)
- python3-dev (for the python3 binding)
- `sudo apt install libc6 libpam-cgfs libcap-dev libapparmor-dev libselinux1-dev libseccomp-dev libgnutls30 liblua5.4-dev python3-dev uidmap`

### LXC Installation
- `sudo apt install lxc lxc-templates lxctl`
- `lxc-checkconfig`
- Possibly
  - `echo 'GRUB_CMDLINE_LINUX=systemd.unified_cgroup_hierarchy=false' > /etc/default/grub.d/cgroup.cfg`
  - `update-grub`

### LXC Install Script
- Runs the above `apt` commands and returns the output of `lxc-checkconfig`

### Setting up an Ethernet bridge
- Get the Ethernet interface name: `ip a`
- Create a bridge that is a master to the Ethernet connection:
  - https://thenewstack.io/how-to-create-a-bridged-network-for-lxd-containers/
  - Copy `managed_files/netplan/99-netplan.yaml` to `/etc/netplan/`
  - Modify the Ethernet adapter name in 2 places to whatever `ip a` returned for this machine
  - `sudo netplan generate`
  - `sudo netplan apply`
- Turn off DHCPCD on the machine
  - https://askubuntu.com/questions/1269837/netplan-bridge-cannot-ping-local-network-devices
  - `sudo systemctl disable dchpcd`
- Run `ip a` again to get the new IP address of the bridge
- Reboot and SSH onto the **new** IP address
  - Wouldn't hurt to give it a permanent lease
- There are other methods:
  - https://www.cyberciti.biz/faq/how-to-add-network-bridge-with-nmcli-networkmanager-on-linux/
  - https://ubuntu.com/blog/converting-eth0-to-br0-and-getting-all-your-lxc-or-lxd-onto-your-lan
    - This one is great for a Raspberry Pi; make sure to turn `dhcpcd` off. Might require reassigning the MAC in ARP and/or reboots all around.


## Repo / Virtual Environment Preparation
- HTTPS: git clone --depth 1 https://github.com/matt-stacey/home-network-config.git
- SSH: git clone git@github.com:matt-stacey/home-network-config.git
- call `source bashrc` from the command line to prep the virtual environment


## Create a Template Container
- `sudo lxc-create -t download -n <privileged-container>`
- Attach to the container: `lxc-attach -n <privileged-container>`
- Basic configuration
    - `sudo apt update`
    - `sudo apt install curl git`
- Configure with the Salt bootstrapper: https://docs.saltproject.io/salt/install-guide/en/latest/topics/bootstrap.html#install-bootstrap
    - `curl -o bootstrap-salt.sh -L https://bootstrap.saltproject.io`
    - `chmod +x bootstrap-salt.sh`
    - RPi: add GPG key
    - Minion: `./bootstrap-salt.sh -A <master IP>`
    - Master and Minion: `./bootstrap-salt.sh -M -A <master IP>`
    - Pip-based, for Ubuntu: `./bootstrap-salt.sh -P -A <master IP>`
- Complete configuration for copying
    - Disable the minion service: `sudo systemctl stop salt-minion`
    - Remove the minion id and keys in `/etc/salt/pki/minion/`
- Detach: `exit`
- Stop the container for copying: `lxc-stop -n <privileged-container>`
- *Master* Start salt-master service: `systemctl start salt-master`


## Container Creation
- `cd` into *containerization*
- create a container list based on the YAML example
- Run the Python setup in copy mode: `python container_setup.py --copy -C <privileged-container> -Y <your YAML>`
- wait while LXC copies the containers


## Container Configuration
- Run the Python setup in configure mode: `python container_setup.py --configure -Y <your YAML>`
- wait while LXC configures the containers


## Container Activation
- Run the Python setup in activate mode: `python container_setup.py --activate -Y <your YAML>`
- wait while LXC activates the containers
- commands to attach to the containers will be printed out; use these to log in and connect the Salt Minion
    - *Minions* Start minion services: `systemctl start salt-minion`
- *Master* Accept minion keys: `salt-key -L`; `salt-key -A`
- *Master* Test minions:
    - `salt '*' test.version`
    - `salt '*' network.interfaces`
- If changing master (ie switch to a container), on all minions:
    - `sudo systemctl stop salt-minion`
    - `sudo rm /etc/salt/pki/minion/minion_master.pub`
    - `sudo systemctl restart salt-minion`


## Container Deactivation
- Run the Python setup in deactivate mode: `python container_setup.py --deactivate -Y <your YAML>`
- wait while LXC deactivates the containers


## Container Commands
- `lxc-create -t download -n privileged-container`
- `lxc-info -n my-container`
- `lxc-ls -f`
- `lxc-start -n my-container [-d] [-c /dev/tty4 &]`
- `lxc-attach -n my-container`
- `lxc-freeze -n my-container`
- `lxc-unfreeze -n my-container`
- `lxc-copy -n original -N new`  # must be stopped
- `lxc-stop -n my-container`
- `lxc-destroy -n my-container`

