#!/usr/bin/env python3
import time
import sqlite3
import os
import bme680
import RPi.GPIO as GPIO
import requests

DB_PATH = "/home/dani/weather.db"
RAIN_PIN = 17 
HALL_PIN = 27 

def get_open_meteo():
    lat = 48.0490  # Koordináták
    lon = 18.6540
    #kért paramétert
    url = (f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
           f"&current=temperature_2m,relative_humidity_2m,rain,surface_pressure,wind_speed_10m"
           f"&timezone=auto")
    try:
        r = requests.get(url, timeout=10)
        curr = r.json()['current']
        return {
            "temp": curr['temperature_2m'],
            "hum": curr['relative_humidity_2m'],
            "wind": curr['wind_speed_10m'],
            "rain": curr['rain'],
            "pres": curr['surface_pressure']
        }
    except Exception as e:
        print(f"API hiba: {e}")
        return None

def init_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE weather (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                temperature REAL,
                humidity REAL,
                pressure REAL,
                gas REAL,
                rain INTEGER,
                wind_speed REAL
            );
        """)
        conn.commit()
        conn.close()
          

def save_to_db(timestamp, temp, hum, pres, gas, rain, wind, temp_out, hum_out, wind_out, rain_out, pressure_out):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO weather (timestamp, temperature, humidity, pressure, gas, rain, wind_speed, temp_out, hum_out, wind_speed_out, rain_out, pressure_out)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (timestamp, temp, hum, pres, gas, rain, wind, temp_out, hum_out, wind_out, rain_out, pressure_out))
    conn.commit()
    conn.close()

# SZÉLSEBESSÉG MÉRÉSE
RADIUS = 0.07 #7cm-es
CIRCUMFERENCE = 2 * 3.14159 * RADIUS    
CALIBRATION_FACTOR = 2.5 

def measure_wind(duration=5):
    count = 0
    def count_pulse(channel):
        nonlocal count
        count += 1
    

    GPIO.add_event_detect(HALL_PIN, GPIO.FALLING, callback=count_pulse, bouncetime=20)
    
    time.sleep(duration) 
    
    GPIO.remove_event_detect(HALL_PIN)
    
    #számítás
    rps = count / duration
    rpm = rps * 60
    wind_kmh = rps * CIRCUMFERENCE * CALIBRATION_FACTOR * 3.6 
    print(f"Fordulatszám: {rpm:.0f} RPM | Impulzusok: {count}")
    return wind_kmh

def init_sensors():
    # GPIO setup
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RAIN_PIN, GPIO.IN)
    GPIO.setup(HALL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Felhúzó ellenállás kell a Hall-hoz

    # BME680 setup
    try:
        sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
    except:
        sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)
    
    sensor.set_humidity_oversample(bme680.OS_2X)
    sensor.set_pressure_oversample(bme680.OS_4X)
    sensor.set_temperature_oversample(bme680.OS_8X)
    sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
    sensor.set_gas_heater_temperature(320)
    sensor.set_gas_heater_duration(150)
    sensor.select_gas_heater_profile(0)
    
    return sensor

def main():
    init_db()
    sensor = init_sensors()

    print(" Időjárás állomás elindult ")

    try:
        while True:
            # 1. Kültéri adatok lekérése az internetről
            out_data = get_open_meteo()

            # 2. Szélmérés a helyi Hall-szenzorral
            wind_speed_local = measure_wind(5)

            # 3. BME680 szenzor adatainak beolvasása
            if sensor.get_sensor_data() and sensor.data.heat_stable:
                timestamp = time.strftime("%Y-%m-%d %H:%M")
                
                # Saját adatok
                temp_in = sensor.data.temperature
                hum_in = sensor.data.humidity
                pres_in = sensor.data.pressure
                gas_in = sensor.data.gas_resistance

                
                rain_local = 100 if GPIO.input(RAIN_PIN) == GPIO.LOW else 0

                #KIÍRÁS
                print(f"[{timestamp}]")
                print(f"  BENT: {temp_in:.1f}°C, {hum_in:.1f}%, {gas_in/1000:.1f} kOhm")
                
                if out_data:
                    print(f"  KINT (API): {out_data['temp']}°C, Szél: {out_data['wind']} km/h")
                    print(f"  ESŐ: Szenzor: {rain_local}% | API: {out_data['rain']} mm")
                else:
                    print("  KINT (API): Nem sikerült letölteni az adatokat.")
                print("-" * 40)

                #MENTÉS AZ ADATBÁZISBA
                if out_data:
                    save_to_db(
                        timestamp, 
                        temp_in, hum_in, pres_in, gas_in, 
                        rain_local, wind_speed_local,
                        out_data['temp'], out_data['hum'], out_data['wind'], out_data['rain'], out_data['pres']
                    )
                else:
                    save_to_db(
                        timestamp, 
                        temp_in, hum_in, pres_in, gas_in, 
                        rain_local, wind_speed_local,
                        None, None, None, None, None
                    )

            
            time.sleep(295) 

    except KeyboardInterrupt:
        print("\nLeállítás...")
    finally:
        GPIO.cleanup()
        print("GPIO felszabadítva.")

if __name__ == "__main__":
    main()
