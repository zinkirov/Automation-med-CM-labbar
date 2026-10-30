# Arkitekturmotivering och systemdokumentation

**Författare:** Mrakim Zinkirov
**Datum:** 30 oktober 2026
**Kurs:** Automatisering med Configuration Management

## 1. Systemöversikt och verktygsval

Miljön består av tre Ubuntu Server-maskiner i ett QEMU/KVM-nät: `controlnode` kör Ansible och styr `node1` och `node2`. De första labbarna byggde upp SSH-åtkomst, användare, en Nginx-webbserver och MariaDB. I labb 10 driftsätter Ansible en flerskiktsapplikation: Nginx på node1 tar emot trafik på port 8082 och skickar den till Gunicorn och Flask. Flask läser och skriver tjänster och kontroller i MariaDB på node2. En separat G-del visar hur en enkel Python-webbklient på node1 kontaktar ett API på node2.

Ansible passar miljön eftersom kontrollnoden redan når målnoderna via SSH. När jag kör en playbook skickar Ansible uppgifterna till noderna; jag behöver inte installera och underhålla någon särskild Ansible-agent på dem. Puppet använder oftast en agent som regelbundet hämtar en katalog från en server. Det kan vara bra om många noder ska kontrollera sitt tillstånd återkommande, men för två noder och tydliga labbkörningar är Ansibles push-modell enkel att använda. Samtidigt kräver push-modellen att kontrollnoden kan nå noderna när en utrullning görs. Jämförelsen utvecklas i [labb 11](lab11/README.md).

Repot har en mapp per labb, eftersom övningarna ska kunna granskas var för sig. Labb 5 och 6 har exempel på `roles/common` och `roles/webserver` med egna `tasks/`, `templates/`, `defaults/` och `handlers/`. I labb 7 finns `roles/database` och `group_vars/all/vault.yml`. Inventories ligger i respektive labbmapp, medan labb 9 visar ett skriptbaserat inventory. Labb 10 delar VG-utrullningen i `vg.yml`, `vg-db.yml` och `vg-web.yml`. Detta är en modulär kursstruktur; det finns ännu ingen gemensam `roles/`- eller `inventories/`-mapp i repots rot. Vid ett större projekt skulle jag samla återanvändbara roller och miljöspecifika inventories mer centralt.

## 2. Säkerhet och hemligheter

SSH-nycklar används för anslutningen från kontrollnoden, och privata nycklar lagras inte i repot. I labb 4–6 läser `authorized_key` en publik nyckel från kontrollnoden och installerar den åt `devops_admin`. `become: true` används på de uppgifter som behöver systembehörighet, till exempel paketinstallation och skrivning under `/etc`. Användaren behöver fortfarande tillåten sudo-åtkomst, och `-K` används när ett sudo-lösenord efterfrågas. Lösenordsfri SSH betyder inte lösenordsfri sudo.

Labb 7 och 10 skyddar databaslösenord i filer krypterade med Ansible Vault. Playbooken i labb 10 läser `vg/secrets.yml`, skapar databaskontot `monitor_app` för node1 och skriver en miljöfil på node1 med rättigheten `0600`. Databaskontot får bara de behörigheter som appen behöver för databasen `service_monitor`. Känsliga uppgifter har `no_log: true`, så de inte skrivs ut i Ansible-resultat. Vault-lösenordet hålls separat från Git; `.gitignore` exkluderar exempelvis `.vault_pass*` och labb 7:s `pass_file/`. Vault skyddar källkoden, men lösenordet måste också hanteras säkert på målnoden. Intern trafik mellan Flask och MariaDB är inte TLS-krypterad i denna labbmiljö. Vid verklig drift skulle jag även begränsa nätverksåtkomst och använda krypterad trafik.

## 3. Skalbarhet och dynamik

De flesta labbar använder ett statiskt inventory med `node1` som webbserver och `node2` som databasserver. Labb 9 returnerar i stället inventory som JSON från `inventory.py`. Det visar hur Ansible kan få sin serverlista vid körning, även om just detta skript har hårdkodade namn och inte hämtar data från ett externt API. För att skala miljön skulle jag koppla inventoryt till en aktuell källa och lägga nya servrar i rätt grupper. Databas- och webbkoden behöver då använda gruppvariabler i stället för en enskild nods namn eller den första noden i en grupp.

Jinja2-mallar skiljer konfiguration från uppgifter: Nginx-sidan i labb 6 använder facts, villkor och loopar, och labb 10 hämtar node2:s IP från facts när anslutningen konfigureras. I labb 5 finns `defaults/main.yml` för exempelvis webbport och miljölista. Med egna inventories och variabler för utveckling, test och produktion kan samma roll eller playbook återanvändas utan att miljödetaljer hårdkodas. Den uppdelningen är en möjlig utveckling av repot; i den nuvarande labbmiljön finns inte separata Dev-, Test- och Produktionsmiljöer.

## 4. Drift, optimering och återhämtning

Idempotens betyder att en ny körning inte ska göra onödiga ändringar när systemet redan har rätt tillstånd. Jag använder tillstånd som `present`, `started` och `enabled`, samt handlers som bara startar om MariaDB eller Gunicorn och laddar om Nginx när relevant konfiguration ändras. Databasschemat importeras i labb 10 när databasen eller schemafilen ändrats. En upprepad körning av `vg.yml` gav `changed=0` på båda noderna. Den första körningen kan naturligtvis rapportera ändringar.

Före utrullning kan jag köra `--syntax-check` och, där uppgifterna tillåter det, `--check` och `--diff`. Efteråt kontrollerar jag tjänster med `systemctl`, nätverksportar med `ss` och HTTP-svar med `curl`. I Service Monitor kan jag registrera en adress, köra en kontroll och se både senaste status och historik från MariaDB. Jag testade svarande tjänster, en stängd port och återhämtning från anslutningsfel till HTTP 200. Ett HTTP 200 kan dock komma från en sida som visar ett internt fel, så en framtida hälsokontroll bör även verifiera förväntat innehåll.

VG-appens Gunicorn, Nginx och MariaDB är systemd-tjänster som startar igen efter omboot. G-delens Python-skript körs med `nohup` och har inte samma automatiska återstart. Dokumenterade körkommandon, Vault-hantering och upprepade kontroller gör det möjligt att återskapa konfigurationen efter ett fel. För mer robust drift behövs också säkerhetskopior av databasen, återläsningstest, larm och ett sätt att köra kontroller regelbundet.
