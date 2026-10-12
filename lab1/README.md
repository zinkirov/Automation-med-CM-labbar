# Lab 1: Environment Setup and Passwordless SSH

## Goal

Create three Linux VMs, configure passwordless SSH and verify both targets with Ansible ping.

## Setup

I created node1 and node2 using virt-install in the host terminal. I created controlnode using virt-manager. All three use Ubuntu Server 24.04 and the same libvirt default NAT network.

| VM | Role | Target login | Observed IP |
| --- | --- | --- | --- |
| controlnode | Ansible controller | controlnode | Not recorded |
| node1 | Managed server | node1 | 192.168.122.7 |
| node2 | Managed server | node2 | 192.168.122.229 |

Addresses are assigned by DHCP and may change.

## Name resolution

I installed and enabled Avahi on all three VMs:

```bash
sudo apt update
sudo apt install -y avahi-daemon
sudo systemctl enable --now avahi-daemon
```

From controlnode, both tests returned three replies with 0% packet loss:

```bash
ping -c 3 node1.local
ping -c 3 node2.local
```

## SSH keys

On controlnode, I generated an Ed25519 key pair and copied its public key to both target users:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/ansible_lab -C "controlnode-ansible"
ssh-copy-id -i ~/.ssh/ansible_lab.pub node1@node1.local
ssh-copy-id -i ~/.ssh/ansible_lab.pub node2@node2.local
```

I verified SSH key login to both servers. The private key stays on controlnode and is not included in this repository. Local SSH aliases allow ssh node1 and ssh node2.

## Ansible verification

I verified both nodes using the SSH aliases configured on controlnode:

```bash
ansible -i 'node1,node2,' -m ping all
```

Both nodes returned SUCCESS, "changed": false and "ping": "pong". Ansible detected /usr/bin/python3 on both servers. This confirms that SSH authentication and Python module execution work.

![Successful Ansible ping to node1 and node2](screenshots/ansible-ping.png)

Ansible ping checks SSH and Python execution, not ICMP connectivity.

## Reflection

Avahi resolves server names; SSH provides remote login. These are separate functions. I also learned to distinguish host commands from commands run inside a VM.