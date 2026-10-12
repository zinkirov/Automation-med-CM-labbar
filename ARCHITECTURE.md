# Architecture Motivation — Draft

Author: Mrakim Zinkirov

This is an outline, not the completed final architecture report. Complete it after implementing the remaining labs. If aiming for VG, follow the teacher's 500–1000 word requirement.

## 1. System Overview and Tool Choice

Current setup: QEMU/KVM, Ubuntu Server 24.04, one Ansible controller and two managed nodes. Explain Ansible's SSH-based push model and compare it with Puppet or SaltStack. Describe the final inventory, playbook and role structure.

## 2. Security and Secrets

Describe SSH keys, become/sudo permissions and Ansible Vault after they are implemented. Explain which files are excluded from Git and how staged changes are checked.

## 3. Scalability and Dynamic Configuration

Document static and dynamic inventories, variable separation and Jinja2 templates after completing those labs.

## 4. Operations and Recovery

Explain idempotence, handlers, check mode, health checks and recovery using actual results from the completed project.

