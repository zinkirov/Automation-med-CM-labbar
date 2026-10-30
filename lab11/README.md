# Labb 11 – Ansible och Puppet

## Hur når koden målnoderna?

**Ansible använder oftast push.** Jag startar en playbook på `controlnode`. Ansible ansluter till `node1` och `node2` via SSH och utför uppgifterna på de noder som anges i inventoryt. Målnoderna behöver ingen särskild Ansible-agent. I den här labbmiljön bestämmer jag när en körning ska ske.

**Puppet använder vanligtvis pull.** En Puppet-agent körs på varje målnod och kontaktar en Puppet-server. Agenten hämtar en katalog med det önskade tillståndet och tillämpar den lokalt, ofta med jämna mellanrum. Puppet kan också användas utan en central server, men server och agent är den vanliga modellen i jämförelsen.

Skillnaden är alltså vem som tar initiativet: med Ansible skickar kontrollnoden ut arbetet vid körning; med Puppet hämtar agenten sin konfiguration. Båda verktygen försöker se till att systemet får det tillstånd som beskrivs i koden.

## Vad händer om jag ändrar ordningen på raderna?

I en **Ansible-playbook** körs uppgifterna normalt uppifrån och ned inom varje play. Ordningen kan därför ändra resultatet. I labb 10 skapas exempelvis databasen och tabellerna innan webbappen ska använda dem. Om jag försöker starta appen innan nödvändiga paket, filer och inställningar finns på plats kan körningen misslyckas. En handler, till exempel en omstart av MariaDB, körs när den har notifierats och normalt efter de vanliga uppgifterna i playet.

I **Puppet** beskriver jag resurser och deras önskade tillstånd i ett manifest. Puppet bygger en katalog och använder relationer mellan resurser för att avgöra vad som måste ske före något annat. Jag bör därför ange viktiga beroenden uttryckligen, till exempel att ett paket ska finnas innan en tjänst startas. Att bara flytta en rad är inte ett tydligt sätt att uttrycka ett sådant beroende; använd till exempel `require`, `before` eller en relation med en pil. Viss ordning kan även följa av Puppets automatiska beroenden och konfiguration, så man ska inte säga att radordningen *aldrig* spelar roll.

Ett enkelt exempel: i Ansible placerar jag vanligtvis uppgiften **installera Nginx** före **starta Nginx**. I Puppet beskriver jag motsvarande beroende mellan paketet och tjänsten, så att Puppet vet vilken resurs som ska hanteras först.

## Jämförelse

| Område | Ansible | Puppet |
| --- | --- | --- |
| **Arkitektur** | Kontrollnod som ansluter till målnoder via SSH och normalt skickar ut arbetet vid körning (push). Ingen särskild Ansible-agent på målnoderna. | Vanligen Puppet-server och Puppet-agent på varje nod. Agenten hämtar sin katalog och tillämpar den (pull). |
| **Språk och syntax** | Playbooks i YAML. Jinja2 används för mallar och variabler. Uppgifter beskrivs med moduler. | Manifest skrivs i Puppets eget deklarativa språk med resurser, klasser och relationer. |
| **Ordning** | Uppgifter körs normalt i den ordning de står i ett play. | Resursers viktiga ordning uttrycks med beroenden och relationer i katalogen. |
| **Fördelar** | Lätt att börja med i en liten SSH-miljö. Tydligt när utrullningen startas. YAML och playbooks är lätta att läsa. | Agenten kan regelbundet kontrollera och korrigera avvikelser. Passar miljöer där många noder ska hållas konfigurerade löpande. |
| **Nackdelar** | Kräver en fungerande anslutning från kontrollnoden när playbooken körs. Återkommande kontroll kräver schemaläggning eller annan automatisering. | Server och agenter innebär fler delar att installera och sköta. Manifest och beroenden kan kräva mer tid att lära sig. |

## Slutsats

För mina två målnoder passar Ansible bra: jag har redan SSH-åtkomst, ett inventory och playbooks som driftsätter tjänsterna. Om miljön växte och jag ville att varje nod regelbundet skulle kontrollera sin konfiguration utan att jag startar en körning, skulle Puppets agentmodell vara intressant att jämföra närmare. Valet beror på hur miljön ska drivas, inte bara på antalet servrar.
