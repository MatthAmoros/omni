# ==================================
# omni server dockerfile
# ===================================

# Use an official Python runtime as a parent image
FROM python:3-slim-stretch

RUN apt-get update && apt-get install -y \
	nano \
	apt-utils \
	git \
	freetds-dev \
	freetds-bin \
	unixodbc-dev \
	tdsodbc \
	apache2 \
	apache2-dev
# mod_WSGI packaged is not compatible with Python > 3.4 (@ operator not recognized)
# We will add it using pip


#Add FreeTDS to odbc drivers
RUN echo "[FreeTDS]" >> /etc/odbcinst.ini
RUN echo "Description=FreeTDS Driver" >> /etc/odbcinst.ini
RUN echo "Driver=/usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so" >> /etc/odbcinst.ini
RUN echo "Setup=/usr/lib/x86_64-linux-gnu/odbc/libtdsS.so" >> /etc/odbcinst.ini

# Copy the current directory contents into the container at /app
WORKDIR /app
ADD . /app

# Install any needed packages specified in python-pip-list
RUN pip install --upgrade pip
RUN pip install --trusted-host pypi.python.org -r python-pip-list.txt

# Make port 5000 (web server) and 54545 (discovery) (default) available to the world outside this container
EXPOSE 5000
EXPOSE 54545

# Pull from git
RUN git clone http://github.com/SunPaz/omni

# Copy connection string file
COPY connectionString.sql /app/omni/cfg/
# Setting up Apache2 / mod_wsgi
COPY omni.local.conf /etc/apache2/sites-available/
RUN echo "Listen 5000" >> /etc/apache2/ports.conf
RUN a2ensite omni.local
COPY omni.wsgi /app/omni/
RUN mkdir /app/omni/www/
RUN mkdir /app/omni/www/logs
# Setting module WSGI and Python Path
RUN mod_wsgi-express module-config >> /etc/apache2/apache2.conf
#RUN a2enmod wsgi
RUN /etc/init.d/apache2 restart

# Start server
WORKDIR /app/omni
CMD service apache2 start && python /app/omni/discover_client.py && /bin/bash

# Then run docker run --net=host <image>
