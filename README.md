# EGMO Cutoffs Predictor

## O projektu

Projekt nastaja kot zaključna projektna naloga pri predmetu 
Programiranje 1 v 2. letniku študija na Fakulteti za
matematiko in fiziko Univerze v Ljubljani. Glavni cilj
projekta je, da iz nepopolnih podatkov o uspehu tekmovalk
čim bolj zanesljivo napovem meje za medalje na tekmovanju.

---

## Zakaj EGMO?

Odgovor je pravzaprav zelo preprost – EGMO je edina
matematična olimpijada, na kateri se točke tekmovalk na
spletni strani tekmovanja posodabljajo v realnem času. Medalje
se praviloma podeli polovici tekmovalk, barva pa se določi v
razmerju 1:2:3. Prav tako velja, da tekmovalke istih držav
dosegajo primerljive rezultate ne glede na leto tekmovanja,
zaradi česar je sploh mogoče narediti kakršnekoli napovedi.

---

## Opis analiziranja

S [spletne strani tekmovanja](https://www.egmo.org/egmos/egmo10/scoreboard/)
bom najprej naložil podatke o preteklih letih (podatki so
ločeni po letih, na zgornji povezavi so podatki iz leta
2021). Analiziral bom, kako se uradne (evropske) države z
rezultati primerjajo z neuradnimi, in pretekle dosežke
slovenskih tekmovalk. Poskusil bom tudi iz nepopolnih podatkov
napovedati točke vsake tekmovalke posebej in s tem meje za
medalje. Pri tem bom upošteval pretekle uspehe njenih 
rojakinj in, če je posamena tekmovalka na olimpijadi že
sodelovala. Efektivnost napovednika bom preveril na lanskem
[RSS Feedu](https://www.egmo.org/egmos/egmo10/scoreboard/rss.xml),
v katerem so kronološko shranjeni vnosi točk v strežnik.