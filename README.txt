README – Raspberry Pi időjárásállomás
Szakdolgozat projekt

Készítette: Balya Dániel


1. A PROJEKT LEÍRÁSA

A projekt célja egy Raspberry Pi alapú időjárásfigyelő rendszer elkészítése, 
amely valós időben gyűjti és jeleníti meg a mért környezeti adatokat.

A rendszer helyi szenzorok segítségével mér adatokat, valamint internetes API-ból
is lekér időjárási információkat. Az összegyűjtött adatokat SQLite adatbázisba menti,
majd webes felületen grafikonokon jeleníti meg.

Mért adatok:
- hőmérséklet
- páratartalom
- légnyomás
- levegőminőség
- eső érzékelés
- szélsebesség


2. FEJLESZTÉSI KÖRNYEZET

A projekt fejlesztése és tesztelése Raspberry Pi 4 eszközön történt,
Raspberry Pi OS operációs rendszer használatával.

A forráskód közvetlenül a Raspberry Pi eszközön lett írva és szerkesztve.

Használt technológiák:
- Python 3.11
- Flask
- SQLite3
- HTML5
- CSS3
- JavaScript
- Chart.js


3. SZÜKSÉGES KÖNYVTÁRAK

Külső Python könyvtárak:
- Flask
- Requests
- bme680
- RPi.GPIO

Beépített Python modulok:
- sqlite3
- threading
- os
- sys
- time


4. RASPBERRY PI BEÁLLÍTÁSOK

A projekt megfelelő működéséhez az I2C interfészt engedélyezni kell.

Bekapcsolás:

sudo raspi-config

Interfacing Options -> I2C -> Enable

A rendszer újraindítása után a szenzor használhatóvá válik.


5. A PROJEKT FUTTATÁSA

-1. A virtuális környezet aktiválása:

source ~/.virtualenvs/pimoroni/bin/activate

-2. A program indítása:

python3 app.py

-3. A webes felület megnyitása böngészőben:

http://localhost:8080

vagy hálózaton keresztül:

http://RaspberryPi_IP_cím:8080


6. A PROJEKT FELÉPÍTÉSE

app.py
- Flask webszerver
- API végpontok
- adatbázis lekérdezések

weather_logger.py
- szenzorok kezelése
- adatgyűjtés
- Open-Meteo API használata
- adatbázis mentés

index.html
- webes felület
- grafikonok megjelenítése
- valós idejű adatok frissítése

weather.db
- SQLite adatbázis


7. HASZNÁLT KÜLSŐ SZOLGÁLTATÁS

Open-Meteo API:
https://open-meteo.com/

Az API külső időjárási adatokat biztosít:
- külső hőmérséklet
- páratartalom
- szélsebesség
- csapadék
- légnyomás


8. FONTOS INFORMÁCIÓK

- A projekt internetkapcsolatot igényel az Open-Meteo API használatához.
- A weather.db adatbázis első indításkor automatikusan létrejön.
- A rendszer Raspberry Pi GPIO hozzáférést használ.
- A webes grafikonok Chart.js könyvtár segítségével készültek.


9. MEGJEGYZÉS


A projekt oktatási célból, szakdolgozat részeként készült.
