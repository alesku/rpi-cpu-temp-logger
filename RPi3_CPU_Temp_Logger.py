#!/usr/bin/python
# -*- coding: utf-8 -*-

# Das Programm bekommt Temperaturen von RPi3 CPU und speist die ins Datenbank
# für spätere Darstellung auf einer Webseite wie 
# http://localhost/cgi-bin/webgui.py

from subprocess import check_output # Liest Ruckgabe von einer Programm
import sqlite3
import time
import numpy
from datetime import datetime

# Zeit merken um jede 30 sekunden ein Wert zu speichern
sec_alt = datetime.now().second

# Pfad zur Datenbank
dbname = "/var/www/cpuTemp_Database.db"

# Eine leere Liste für laufende Werte erstellen
temp_list = [0]*60

def log_temperature(currentTemp):
	""" Speichern in die SQLite Datenbank.
	Um ein Zugriff auf Datenbank zu haben, muss Python Programm mit Admin Rechte
	gestartet werden."""
	myConnection = sqlite3.connect(dbname)
	myCursor = myConnection.cursor()
	
	myCursor.execute("INSERT INTO temps VALUES (datetime('now', 'localtime'), (?))", (currentTemp,))
	
	myConnection.commit()
	myConnection.close()
		

def abfrage():
	""" Macht CPU-Temperaturabfrage und gibt das Wert zurück, z.B: 53.692
	Temperatursensor liefert Werte mit der Genauigkeit von 0.538°C """
	output = check_output(['cat', '/sys/class/thermal/thermal_zone0/temp'])
	stripedVal = output.strip()
	tempVal = float(stripedVal)/1000
	
	return tempVal
	      
		
def main():
	while True:
		for i in range(60):
			sec=datetime.now().second
			
			tempValue = abfrage()
			temp_list.pop(0)
			temp_list.append(tempValue)
			time.sleep(1)
			
			averageTempWert = round(numpy.mean(temp_list), 1)
						
			if sec % 30 == 0 and sec != sec_alt: 
				# Neues Wert wird jede 30 Sekunden ins Datenbank geschrieben
				log_temperature(averageTempWert)
			
			sec_alt = sec
	
if __name__ == "__main__":
	main()
