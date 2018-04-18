#!/bin/bash

sudo apt-get update
sudo apt-get install freetds-dev freetds-bin unixodbc-dev tdsodbc
#On Raspberry only
echo "[FreeTDS]\n\
Description = FreeTDS unixODBC Driver\n\
Driver = /usr/lib/arm-linux-gnueabihf/odbc/libtdsodbc.so\n\
Setup = /usr/lib/arm-linux-gnueabihf/odbc/libtdsodbc.so" >> /etc/odbcinst.ini

pip install pyodbc
