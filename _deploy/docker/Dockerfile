# ==================================
# omni server dockerfile
# ===================================

# Use an official Python runtime as a parent image
FROM python:3

RUN apt-get update && apt-get install -y \
	nano \
	apt-utils \
	git \
	freetds-dev \
	freetds-bin \
	unixodbc-dev \
	tdsodbc

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

# Make port 5000 (web server) and 54545 (discovery)  (default) available to the world outside this container
EXPOSE 5000
EXPOSE 54545

# Pull from git
RUN git clone http://github.com/SunPaz/omni

# Copy connection string file
COPY connectionString.sql /app/omni/cfg/

# Start server
WORKDIR /app/omni
CMD ["python", "./server.py"]
