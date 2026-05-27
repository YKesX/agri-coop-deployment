# Libvirt Networks for Phase 2 Virtualization Demo

## Define and start networks

```bash
# Public network (NAT-forwarded, simulates AWS public subnet)
sudo virsh net-define agri-public-net.xml
sudo virsh net-start agri-public-net
sudo virsh net-autostart agri-public-net

# Private network (isolated, simulates AWS private subnet)
sudo virsh net-define agri-private-net.xml
sudo virsh net-start agri-private-net
sudo virsh net-autostart agri-private-net
```

## Verify

```bash
virsh net-list --all
```

## VM management cheat sheet

```bash
# Create a snapshot
virsh snapshot-create-as <vm-name> --name "before-docker-install" --description "Clean state"

# List snapshots
virsh snapshot-list <vm-name>

# Revert to a snapshot
virsh snapshot-revert <vm-name> --snapshotname "before-docker-install"

# Clone a VM
virt-clone --original <vm-name> --name <new-vm-name> --auto-clone

# Adjust CPU (live + persistent)
virsh setvcpus <vm-name> 2 --live --config

# Adjust memory (must set max first, then current)
virsh setmaxmem <vm-name> 2G --config
virsh setmem <vm-name> 2G --config
```
