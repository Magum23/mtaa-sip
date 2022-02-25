# Zadanie 1 – SIP Proxy (telefónna ústredňa)
## Hlavná myšlienka zadania:
Na vašom počítači (alebo virtuálnom počítači) sprevádzkujte SIP Proxy, ktorá
umožní prepájanie a realizáciu hovorov medzi štandardnými SIP klientami.
Doplňujúce informácie k zadaniu:
Na implementáciu vašej SIP Proxy si môžete zvoliť akýkoľvek programovací jazyk a použiť akúkoľvek SIP
knižnicu, ktorá pre daný programovací jazyk existuje. Vo výsledku však musíte spúšťať “váš kód”, v
ktorom sú zakomponované knižnice, ktoré poskytujú funkcionalitu SIP Proxy. To znamená, že nemôžete
zobrať existujúcu SIP Proxy ako napr. Asterisk, kde len skompilujete alebo priamo spustíte cudziu
binárku… Hovor musí byť realizovaný medzi dvomi fyzickými zariadeniami v rámci LAN siete.
## Rozsah povinných funkcionalít:
-Registrácia účastníka (bez nutnosti autentifikácie)
-Vytočenie hovoru a zvonenie na druhej strane
-Prijatie hovoru druhou stranou, fungujúci hlasový hovor
-Ukončenie hlasového hovoru (prijatého aj neprijatého)

Ak sú splnené všetky tieto podmienky, študent získava 5 bodov, ktoré sú minimom na absolvovanie
tohoto zadania.
## Doplnkové funkcionality (ktoré môžete, ale nemusíte urobiť):
-Možnosť zrealizovať konferenčný hovor (aspoň 3 účastníci)
-Možnosť presmerovať hovor
-Možnosť realizovať videohovor
-Logovanie “denníka hovorov” – kto kedy komu volal, kedy bol ktorý hovor prijatý, kedy bol ktorý hovor ukončený, do ľubovoľného textového súboru v ľubovoľnom formáte
-Úprava SIP stavových kódov z zdrojovom kóde proxy, napr. “486 Busy Here” zmeníte na “486 Obsadené”
Každá doplnková funkcionalita predstavuje plus 1 bod.
Počas prezentácie zadania musíte byť schopní na zariadení, kde beží ústredňa urobiť SIP trace a otvoriť
ho pomocou tcpdump alebo Wireshark, a v primeranom rozsahu vysvetliť cvičiacemu, ako daná
signalizácia prebieha.
##Forma odovzdania:
-Dokumentácia, kde opíšete, ako ste vase riešenie implementovali, aké knižnice ste použili, a ako ste ústredňu sprevádzkovali, vo formáte PDF do miesta odovzdania v AIS. V PDF dokumente musí yť odkaz na váš repozitár v Gite (verejný rezpoitár, ľubovoľná služba)
-Vo vašom repozitári sa musí nachádzať PCAP trace z každého scenára, ktorý vaša implementácia poskytuje.

## Termín odovzdania:
1.3.2022 23:59 do miesta odovzdania v AIS
## Užitočné odkazy:
### Zoznam SIP knižníc pre rôzne programovacie jazyky (v sekcii SIP Protocol Stacks and Libraries):
- https://www.voip-info.org/open-source-voip-software/
### Odporúčané SIP klienty na testovanie hovorov:
- Linphone: https://www.linphone.org/
- Zoiper: https://www.zoiper.com/
- Jitsi: https://desktop.jitsi.org/Main/Download.html
- Ďalšie sú tu, v sekcii SIP Clients: https://www.voip-info.org/open-source-voip-software/
