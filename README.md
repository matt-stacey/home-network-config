# home_salt
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
       
### Installation
- `sudo apt install lxc lxc-templates lxctl`
- `lxc-checkconfig`
- `echo 'GRUB_CMDLINE_LINUX=systemd.unified_cgroup_hierarchy=false' > /etc/default/grub.d/cgroup.cfg`
- `update-grub`


## Repo / Virtual Environment Preparation
- HTTPS: git clone --depth 1 https://github.com/matt-stacey/home_salt.git
- SSH: git clone git@github.com:matt-stacey/home_salt.git
- call `source bashrc` from the command line to prep the virtual environment


## Template Container
- `sudo lxc-create -t download -n <privileged-container>`
- Attach to the container: `lxc-attach -n <privileged-container>`
- Basic configuration
    - `sudo apt update`
    - `sudo apt install curl`
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
- `cd` into *containerization* create a container list based on the template
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
