#!/bin/bash
sudo apt-get updated
sudo apt-get install pip

#FreeTDS + ODBC
sudo apt-get install freetds-dev freetds-bin unixodbc-dev tdsodbc

#On Raspberry only
sudo echo "[FreeTDS]\n\
Description = FreeTDS unixODBC Driver\n\
Driver = /usr/lib/arm-linux-gnueabihf/odbc/libtdsodbc.so\n\
Setup = /usr/lib/arm-linux-gnueabihf/odbc/libtdsodbc.so" >> /etc/odbcinst.ini

sudo pip install flask
sudo pip install pyodbc
sudo pip install RPi.GPIO -g
