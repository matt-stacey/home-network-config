# ensure that the salt-master container has this mounted properly in /var/lib/lxc/<container>/config with:
# Mounted drives
# lxc.mount.entry = /root/Git/salt/pillar srv/pillar none bind 0 0

base:
    '*':
        - default  # pillar/default.sls

{% set under_id = grains['id'].replace(".","_") %}

    '{{grains.id}}':
        - ignore_missing: True
        - hosts.{{under_id}}  # pillar/hosts/<host>.sls
