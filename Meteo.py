from pyA20.gpio import gpio
from pyA20.gpio import port

import dht
import time
import datetime
import eel
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# Test komunikacie medzi javascriptom a pythonom
@eel.expose 
def say_hello_py(x):
    print('Hello from %s' % x)

say_hello_py('Python World!')

# Funkcia ktora sa zavola pri zatvoreni okna v prehliadaci
def callback_end(route, websockets):
    print('Uzivatel sa odpojil')
# Test kanalu
def callback(channel):
    print('Daco sa deje')
# Vypocet priemeru listu
def Average(lst):
    return sum(lst) / len(lst)
# Nastavenia siete
my_options = {
    'mode': False,
    'host': '192.168.1.109',
    'port': 8000,
    'close_callback': callback_end,
    'block': False
}
# Start servera
eel.init('web')
eel.start("index.html", suppress_error=True, options = my_options)
   
# Inicializacia portu GPIO
PIN2 = port.PA0
gpio.init()

instance = dht.DHT(pin=PIN2)

# Listy pre teploty v hodine, dni a tyzdni
tempshour = []
humiditieshour = []

tempsday = []
humiditiesday = []

tempsweek = []
humiditiesweek = []

# Priemerne teploty za hodinu, den a tyzden 
temphouravg = 0
humhouravg = 0

tempdayravg = 0
humdayavg = 0

tempweekavg = 0
humweekavg = 0

# Posledna minuta, hodina, den zaznamu
lastMin = datetime.datetime.now().minute-1
lastHour = datetime.datetime.now().hour-1
lastDay = datetime.datetime.now().day-1

# Nekonecny cyklus
while True:
    # Citanie zo senzora
    result = instance.read()
    # Ak je vysledok citania spravny sprav toto
    if result.is_valid():
        # Aktualny cas pocas merania
        currenttime = datetime.datetime.now()
        # Vyber hodnot teploty a vlhosti
        temp = int(result.temperature)
        hum = int(result.humidity)

        print("Last valid input: " + str(currenttime))
        print(temp)
        print(hum)
        # Kazdu minutu ktora je rozdielna od poslednej ulozenej
        if lastMin != currenttime.minute:
            # Nastavenie minuty ako poslednej
            lastMin = currenttime.minute
            # Pridanie hodnot do listu
            tempshour.append(temp)
            humiditieshour.append(hum)
            # 
            if(len(tempshour)>60):
                tempshour = tempshour[1:]
                humiditieshour = humiditieshour[1:]

            # Graf pre teplotu
            plt.figure(figsize=(6.00, 3.0), dpi=100)
            plt.plot(tempshour)
            plt.ylabel('Teplota [°C]')
            plt.grid(axis = "y")
            plt.xticks(np.linspace(0, 60, num=6))
            plt.yticks([0, 10, 20, 30, 40])
            plt.tight_layout()
            plt.savefig('web/temp/'+"temphour"+'.png')
            plt.close()

            # Graf pre vlhkost
            plt.figure(figsize=(6.00, 3.0), dpi=100)
            plt.plot(humiditieshour)
            plt.ylabel('Vlhkosť [%]')
            plt.grid(axis = "y")
            plt.xticks(np.linspace(0, 60, num=6))
            plt.yticks([0, 10, 20, 30, 40])
            plt.tight_layout()
            plt.savefig('web/temp/'+"humhour"+'.png')
            plt.close()

            temphouravg = Average(tempshour)
            humhouravg = Average(humiditieshour)

        if lastHour != currenttime.hour:
            lastHour = currenttime.hour
            tempsday.append(temphouravg)
            humiditiesday.append(humhouravg)

            if(len(tempsday)>24):
                tempsday = tempsday[1:]
                humiditiesday = humiditiesday[1:]

            plt.figure(figsize=(6.00, 3.0), dpi=100)
            plt.plot(tempsday)
            plt.ylabel('Teplota [°C]')
            plt.grid(axis = "y")
            plt.xticks(np.linspace(0, 24, num=4))
            plt.yticks([0, 10, 20, 30, 40])
            plt.tight_layout()
            plt.savefig('web/temp/'+"tempday"+'.png')
            plt.close()

            plt.figure(figsize=(6.00, 3.0), dpi=100)
            plt.plot(humiditiesday)
            plt.ylabel('Vlhkosť [%]')
            plt.grid(axis = "y")
            plt.xticks(np.linspace(0, 24, num=4))
            plt.yticks([0, 10, 20, 30, 40])
            plt.tight_layout()
            plt.savefig('web/temp/'+"humday"+'.png')
            plt.close()

            tempdayravg = Average(tempsday)
            humdayavg = Average(humiditiesday)

        if lastDay != currenttime.day:
            lastDay = currenttime.day
            tempsweek.append(tempdayravg)
            humiditiesweek.append(humdayavg)

            if(len(tempsweek)>7):
                tempsweek = tempsweek[1:]
                humiditiesweek = humiditiesweek[1:]

            plt.figure(figsize=(6.00, 3.0), dpi=100)
            plt.plot(tempsweek)
            plt.ylabel('Teplota [°C]')
            plt.grid(axis = "y")
            plt.xticks(np.linspace(1, 7, num=7))
            plt.yticks([0, 10, 20, 30, 40])
            plt.tight_layout()
            plt.savefig('web/temp/'+"tempweek"+'.png')
            plt.close()

            plt.figure(figsize=(6.00, 3.0), dpi=100)
            plt.plot(humiditiesweek)
            plt.ylabel('Vlhkosť [%]')
            plt.grid(axis = "y")
            plt.xticks(np.linspace(1, 7, num=7))
            plt.yticks([0, 10, 20, 30, 40])
            plt.tight_layout()
            plt.savefig('web/temp/'+"humweek"+'.png')
            plt.close()
            
            tempweekavg = Average(tempsweek)
            humweekavg = Average(humiditiesweek)
        # Aktualizuj web
        eel.say_hello_js(temp, hum, "{:3.1f}".format(temphouravg), "{:3.1f}".format(humhouravg), "{:3.1f}".format(tempdayravg), "{:3.1f}".format(humdayavg), "{:3.1f}".format(tempweekavg), "{:3.1f}".format(humweekavg))
    # Cakaj sekundu
    eel.sleep(1.0)
 