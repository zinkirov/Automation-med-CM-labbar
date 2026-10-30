# Automatisering med Ansible – labbar 1–12

**Författare:** Mrakim Zinkirov

Detta repo samlar kursens labbar i separata mappar. Labb 1–10 innehåller miljö, playbooks, roller, inventering, Vault, CMDB och en driftsatt applikation. Labb 11 jämför Ansible och Puppet. Labb 12 sammanfattar projektet; den samlade motiveringen finns i [ARCHITECTURE.md](ARCHITECTURE.md).

## Labbmiljö och förutsättningar

- En kontrollnod (`controlnode`) och två hanterade Ubuntu Server 24.04-noder (`node1`, `node2`) på ett QEMU/KVM-nät.
- Ansible på kontrollnoden samt SSH-åtkomst till båda noderna. Inventories använder nodnamnen `node1` och `node2`; justera namn, IP och SSH-användare efter din miljö.
- Användaren som kör playbooks behöver `sudo` på målnoderna. Ange lösenord med `-K` där det behövs.
- Samlingarna `ansible.posix` (SSH-nyckeluppgifterna) och `community.mysql` (MariaDB-uppgifterna) behövs. Installera vid behov med `ansible-galaxy collection install ansible.posix community.mysql`.
- Labb 4–6 läser den **publika** nyckeln `~/.ssh/devops_admin.pub` på kontrollnoden. Labb 7 och 10 använder skilda Vault-filer; du behöver rätt Vault-lösenord för respektive fil.

Kör kommandona från **den angivna labbmappen**. Varje labb har egna filer och flera har en egen `ansible.cfg` med `inventory = inventory.ini`. Detta repo innehåller ingen gemensam playbook som heter `site.yml` i roten.

## Struktur och körning

| Labb | Innehåll | Exempel på körning från labbmappen |
| --- | --- | --- |
| [1](lab1/README.md) | Tre VM:ar, SSH och första inventoryt | `ansible -i inventory.ini all -m ping` |
| [2](lab2/README.md) | Ad hoc-kommandon | `ansible -i ../lab4/inventory.ini all -m command -a 'df -h /'` |
| [3](lab3/README.md) | Nginx och idempotens | `ansible-playbook -i ../lab4/inventory.ini web.yml -K` |
| [4](lab4/README.md) | Användare och publik SSH-nyckel | `ansible-playbook users.yml -K` |
| [5](lab5/README.md) | Återanvändbara roller | `ansible-playbook site.yml -K` |
| [6](lab6/README.md) | Facts och Jinja2-mallar | `ansible-playbook site.yml -K` |
| [7](lab7/README.md) | Vault och MariaDB-roll | `ansible-playbook database.yml -K --ask-vault-pass` |
| [8](lab8/README.md) | CMDB-rapporter | `ansible-playbook cmdb.yml` |
| [9](lab9/README.md) | Skriptbaserat inventory | `ansible-inventory -i ./inventory.py --list` |
| [10](lab10/README.md) | Python-API (G) och Service Monitor (VG) | `ansible-playbook vg.yml -K --ask-vault-pass` |
| [11](lab11/README.md) | Ansible jämfört med Puppet | Läs Markdownfilen; ingen playbook krävs. |
| [12](lab12/README.md) | Slutlig sammanställning | Se [arkitekturmotiveringen](ARCHITECTURE.md). |

För den enklare Vault-övningen i labb 7 används `ansible-playbook secrets.yml -K --ask-vault-pass`. För G-delen i labb 10 används `ansible-playbook playdebug.yml` från `lab10/`. Labb 5 och 6 har varsin version av samma roll; de körs separat. Läs respektive labbs README för resultat och skärmbilder.

## Kontroll efter driftsättning

Kör på kontrollnoden från `lab10/` efter att inventoryt har anpassats:

```bash
ansible all -m ping
ansible-playbook vg.yml --syntax-check --ask-vault-pass
ansible-playbook vg.yml -K --ask-vault-pass
ansible-playbook vg.yml -K --ask-vault-pass
curl -i http://node1.local:8082/api/services
```

Den andra körningen av `vg.yml` kontrollerar idempotens. I min labbmiljö gav en upprepad körning `changed=0` på båda noderna. Kontrollera också webbgränssnittet på `http://node1.local:8082/`, att en ny tjänst går att registrera och att kontrollhistoriken sparas i MariaDB. `--check` ger en förhandsvisning för lämpliga uppgifter, men kan inte ensamt verifiera en ny installation där paket och tjänster ännu saknas.

## Säkerhet och begränsningar

Privata SSH-nycklar och Vault-lösenord hör inte hemma i Git. Databaslösenorden ligger i Vault-krypterade filer (`lab7/group_vars/all/vault.yml` och `lab10/vg/secrets.yml`); `.gitignore` utesluter bland annat `.vault_pass*`, `pass_file/`, loggar och `.retry`. Labb 7:s `secrets.yml` är en playbook, trots filnamnet. Granska alltid `git status` och `git diff --cached` före commit.

Service Monitor är en labbapplikation utan inloggning eller HTTPS på det interna webbgränssnittet. Den gör HTTP-kontroller på begäran; den har inga schemalagda kontroller eller larm. Inkommande adresser bör begränsas innan appen används utanför labbnätet. Labb 9:s inventoryskript returnerar en dynamisk JSON-struktur men har fortfarande en hårdkodad serverlista.
