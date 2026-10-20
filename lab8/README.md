# Labb 8 – CMDB och Configuration Items

## Genomförande

Jag skapade [cmdb.yml](cmdb.yml) som samlar in information från node1 och node2. Servrarna är Configuration Items (CIs), och deras egenskaper dokumenteras i varsin Markdown-rapport.

`gather_facts: true` hämtar hostname, OS-version, RAM, CPU, IP-adresser, upptid och diskstorlek. Uppgiften `ansible.builtin.package_facts` samlar dessutom in installerade paket innan rapporten skapas.

[Jinja2-mallen](templates/inventory_report.md.j2) används av `ansible.builtin.template`. `delegate_to: localhost` gör att rapporterna skrivs på controlnode med respektive nods information. Nodnamnet i filnamnet gör att rapporterna inte skriver över varandra.

## Körning och resultat

Kör från labbmappen på controlnode, där SSH-anslutningarna till node1 och node2 är konfigurerade:

```bash
mkdir -p reports
ansible-playbook cmdb.yml --syntax-check
ansible-playbook cmdb.yml
```

Körningen med paketinsamling lyckades på båda noderna: `ok=3`, `changed=1`, `unreachable=0`, `failed=0`.

- [Rapport för node1](reports/inventory_reportnode1.md): 2 vCPU, 1967 MB RAM totalt, disk vda 20 GB och 710 paketnamn.
- [Rapport för node2](reports/inventory_reportnode2.md): 2 vCPU, 1967 MB RAM totalt, disk vda 20 GB och 746 paketnamn.

Båda rapporterna innehåller totalt och fritt RAM, IPv4- och IPv6-adresser samt upptid. Upptiden visas i timmar efter godkännande från läraren. Paketnamnen sorteras alfabetiskt med en Jinja2-loop. Disknamnet `vda` gäller de aktuella labbnoderna.

Rapporterna är ögonblicksbilder från insamlingen. Fritt RAM och upptid förändras, vilket kan ge `changed` vid nästa körning även om serverkonfigurationen är oförändrad.

## VG – relationer och beroenden

Enligt lärarens instruktion utgår analysen från ett tänkt scenario: en webbapplikation på **node1** använder MariaDB på **node2**. Applikationskopplingen är inte implementerad i labbmiljön.

**Beroenderiktning: node1 → node2.** Applikationen skickar databasfrågor till node2 för inloggning samt läsning och lagring av användaruppgifter.

| Fel | Konsekvens |
|---|---|
| Node2 eller MariaDB stannar | Databasberoende funktioner som inloggning, läsning och sparande slutar fungera. Statiska sidor kan fortfarande visas. |
| Node1 stannar | Användarna kommer inte åt webbapplikationen. MariaDB på node2 kan fortsätta köra och lagrade data finns kvar. |
| Nätverksförbindelsen mellan noderna bryts | Båda servrarna kan vara igång, men applikationen når inte databasen. Databasberoende funktioner slutar fungera. |

Applikationen är beroende av både databastjänsten och nätverksanslutningen till node2. Databasen behöver däremot inte webbapplikationen för att fortsätta köra. Controlnode använder dessutom SSH till båda noderna för administration; om controlnode stannar kan dessa Ansible-körningar inte göras, men de redan startade tjänsterna kan fortsätta köra.
