# Labb 12 – summering och slutlig arkitekturmotivering

Projektets labbar ligger i mapparna `lab1/`–`lab11/`. Rotens [README.md](../README.md) beskriver miljö, förutsättningar och de kommandon som hör till respektive labb. [ARCHITECTURE.md](../ARCHITECTURE.md) motiverar verktygsval, struktur, säkerhet, skalbarhet, verifiering och återhämtning utifrån det som faktiskt finns i repot.

## Slutlig kontroll på kontrollnoden

Kör från respektive labbmapp, med SSH, sudo, relevanta Ansible-samlingar och Vault-lösenord tillgängliga:

```bash
cd lab10
ansible all -m ping
ansible-playbook vg.yml --syntax-check --ask-vault-pass
ansible-playbook vg.yml -K --ask-vault-pass
ansible-playbook vg.yml -K --ask-vault-pass
curl -i http://node1.local:8082/api/services
```

Den andra körningen visar om utrullningen är idempotent. Kontrollera därefter att webbgränssnittet på port 8082 kan lägga till en tjänst och spara en ny kontroll i MariaDB. Tidigare körning av labb 10 gav `changed=0` på båda noderna; kommandona ovan måste verifieras på nytt på den kontrollnod där den slutliga inlämningen körs. Använd `--check` som en kompletterande förhandskontroll, inte som ersättning för en riktig utrullning.

## Avgränsning

Labbarna har egna inventories och playbooks. Roten har ingen gemensam `site.yml` som driftsätter alla labbar samtidigt. För labb 5, 6 och 10 används Nginx på samma nod: Nginx-mallarna i labb 5 och 6 behåller inkluderingen av `sites-enabled` så att labb 10:s webbplats fortfarande kan läsas. Verifiera den kombinationen på node1 efter att filerna kopierats till kontrollnoden.
