#!/bin/bash
sudo apt-get updated
#Python + pip package manager
sudo apt-get install python python-dev pip

#FreeTDS + ODBC
sudo apt-get install freetds-dev freetds-bin unixodbc-dev tdsodbc

#On Raspberry only
sudo echo "[FreeTDS]\n\
Description = FreeTDS unixODBC Driver\n\
Driver = /usr/lib/arm-linux-gnueabihf/odbc/libtdsodbc.so\n\
Setup = /usr/lib/arm-linux-gnueabihf/odbc/libtdsodbc.so" >> /etc/odbcinst.ini

#Python packages : Flask (Web Framework), pyODBC (ODBC drivers for python), RPi.GPIO (Raspberry GPIO access), pySHA3 (Cryptography package)
sudo pip install flask
sudo pip install pyodbc
sudo pip install RPi.GPIO -g
sudo pip install pysha3
