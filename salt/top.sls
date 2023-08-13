# ensure that the salt-master container has this mounted properly in /var/lib/lxc/<container>/config with:
# Mounted drives
# lxc.mount.entry = /root/Git/salt/salt srv/salt none bind 0 0

base:
    '*':
        - minion  # salt/minion.sls

    '{{grains.id}}':
        - roles.{{pillar.get('role', '')}}  # roles/<role>.sls
