# Configuration Management with Ansible

Author: Mrakim Zinkirov

Private course repository. Each lab has its own folder containing a short report, relevant code and required screenshots.

## Environment

- Host: Kubuntu with QEMU/KVM and libvirt.
- Three Ubuntu Server 24.04 VMs: controlnode, node1 and node2.
- Each VM: 2 vCPUs, 2 GB RAM and a 20 GB virtual disk.
- Shared libvirt default NAT network. The teacher approved this setup provided the VMs can communicate.
- Ansible runs on controlnode. Avahi provides .local names.

## Run the Lab 1 test

Run on controlnode, where the private SSH key is stored:

```bash
ansible -i lab1/inventory.ini all -m ansible.builtin.ping
```

Prerequisites: Ansible installed, all VMs running, .local resolution working, public key installed on both targets. Inventory assumes target usernames node1 and node2.

## Status

Lab 1 completed: both nodes returned SUCCESS and ping: pong. The result screenshot is included in lab1/screenshots/. Labs 2–12 are not completed.

## Security

Never commit private SSH keys, passwords, tokens, VM disks or ISO files. Keep secrets in Ansible Vault when required. A private repository is not a substitute for secret protection. Review staged files before every commit; .gitignore does not remove files already tracked by Git.

ARCHITECTURE.md is a draft to complete as the project develops.

