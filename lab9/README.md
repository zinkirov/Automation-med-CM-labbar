# Labb 9 – Dynamiska inventories och API-koppling

## Syfte

Syftet var att förstå hur Ansible kan läsa en serverlista från ett körbart skript i stället för en statisk inventoryfil. Ett Python-skript skapades för att returnera ett inventory i JSON-format. Därefter verifierades strukturen med `ansible-inventory` och anslutningen till båda noderna med en ad-hoc-körning av modulen `ping`.

## Labbmiljö

| Del | Användning |
|---|---|
| `controlnode` | Kör Python-skriptet och Ansible-kommandona |
| `node1` | Hanterad nod |
| `node2` | Hanterad nod |
| `labservers` | Inventorygrupp som innehåller båda noderna |
| `~/ansible-dag9` | Arbetskatalog på controlnode |

Den befintliga SSH-åtkomsten till noderna användes.

## Implementation

Filen `inventory.py` innehåller följande kod:

```python
#!/usr/bin/env python3
import json

inventory = {
    "labservers": {
        "hosts": ["node1", "node2"]
    },
    "_meta": {
        "hostvars": {}
    }
}

print(json.dumps(inventory))
```

Variabeln `inventory` är en Python-dictionary. Funktionen `json.dumps()` omvandlar den till JSON och `print()` skriver resultatet till standardutmatningen, där Ansible kan läsa det. Gruppen `labservers` innehåller `node1` och `node2`. Under `_meta.hostvars` kan värdspecifika variabler anges; inga sådana variabler definierades i detta skript.

Skriptet gjordes körbart med:

```bash
chmod +x inventory.py
```

Vid verifieringen angavs inventorykällan uttryckligen med `-i ./inventory.py`. Därmed användes skriptet som inventorykälla för båda Ansible-kommandona.

## Genomförande och resultat

### 1. Kontroll av skriptets JSON-utdata

```bash
python3 inventory.py
```

Resultat:

```json
{"labservers": {"hosts": ["node1", "node2"]}, "_meta": {"hostvars": {}}}
```

Under arbetet uppstod först felet `NameError: name 'inventory' is not defined`. Orsaken var att dictionaryn inte hade tilldelats variabelnamnet `inventory`. Felet löstes genom att lägga till `inventory =` före strukturen. Därefter skrev skriptet ut JSON korrekt.

### 2. Verifiering med Ansible

```bash
ansible-inventory -i ./inventory.py --list
```

Resultat:

```json
{
    "_meta": {
        "hostvars": {}
    },
    "all": {
        "children": [
            "ungrouped",
            "labservers"
        ]
    },
    "labservers": {
        "hosts": [
            "node1",
            "node2"
        ]
    }
}
```

Ansible läste skriptets utdata och identifierade båda noderna i gruppen `labservers`. Grupperna `all` och `ungrouped` lades till i Ansibles bearbetade inventory.

### 3. Ad-hoc-test mot noderna

```bash
ansible -i ./inventory.py labservers -m ping
```

Resultat:

```text
node2 | SUCCESS => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python3"
    },
    "changed": false,
    "ping": "pong"
}
node1 | SUCCESS => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python3"
    },
    "changed": false,
    "ping": "pong"
}
```

Båda noderna svarade med `SUCCESS` och `"ping": "pong"`. Resultatet verifierar att Ansible kunde ansluta via SSH och köra Python-modulen på båda noderna. Detta är ett Ansible-test och inte en vanlig ICMP-ping. Värdet `"changed": false` visar att testet inte rapporterade någon ändring på noderna.

## Avgränsning och koppling till API:er

Lösningen använder Ansibles gränssnitt för ett skriptbaserat inventory, men servernamnen är hårdkodade. Inget externt API anropades i denna labb. Instruktionerna krävde ett skript som returnerar JSON, verifiering av inventoryt och ett ping-test.

I en vidareutveckling kan skriptet hämta servernamn, IP-adresser och grupper från exempelvis en molntjänst eller en CMDB via ett API och omvandla svaret till samma JSON-struktur.

Ansible kan anropa inventoryskript med `--list`. Den enkla implementationen läser inte kommandoradsargument utan skriver alltid ut hela inventoryt, vilket fungerade i de redovisade testerna. En mer generell implementation bör hantera argument och fel uttryckligen. `_meta.hostvars` gör det möjligt att lämna värdvariabler tillsammans med hela inventoryt.

## Slutsats

Labbens tre praktiska moment genomfördes: ett Python-skript returnerade ett JSON-inventory, Ansible läste strukturen och båda noderna svarade på ad-hoc-testet. Lösningen visar hur en serverlista kan levereras till Ansible vid körning och ger en grund för att senare ersätta den hårdkodade listan med data från en extern källa.

## Redovisningsfiler

| Fil | Innehåll |
|---|---|
| `README.md` | Labbrapport med implementation, resultat och slutsats |
| `inventory.py` | Körbart Python-skript som returnerar inventoryt |
| `ansible.cfg` | Lokal Ansible-konfiguration |
| `inventory-output.txt` | Sparad utdata från inventoryverifieringen |
| `ping-output.txt` | Sparad utdata från ping-testet |
