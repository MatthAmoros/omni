# Omni

Omni aims to be a centralized Factory 4.0 controller.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Installing client module

On your raspberry Pi board :
Python / Packet Manager (pip) and main packages (RPi.GPIO)
```
git clone http://github.com/SunPaz/omni
cd _deploy
chmod 740 delpoy_requiered_modules.sh
sh delpoy_requiered_modules.sh
```
## Running the tests

Post installation checks can be ran like this :

```
cd _deploy
python test_python_packages.py
```

## Installing server application

To deploy server application :

Navigate to "./cfg/" and edit file connectionString.example with your database credentials then save it in "./_deploy/docker/connectionString.sql".
Note : To deploy database, you can use the script located in "./_deploy/database/".

Navigate to "./_deploy/docker/" and then execute the following docker commands :

```
docker build . -t omni-server
docker run -it --entrypoint=/bin/bash --net=host omni-server
docker ps
```

## Basic setup

TODO

## Supported devices / roles

Role : Access controller
  - HID iClass R-640X-300
  - RC522 Reader
  - [TODO] ZK4500
  - [TODO] Digital Persona URU 4000

Role : Energy Manager
  - [TODO]


## Built With

* [Flask](http://flask.pocoo.org/docs/0.12/) - Flask is a micro webdevelopment framework for Python.
* [RPi.GPIO](https://pypi.org/project/RPi.GPIO/) - Provides a class to control the GPIO on a Raspberry Pi.
* [MFRC522](https://github.com/pimylifeup/MFRC522-python) - MFRC522 Wrapper
* [Docker](https://www.docker.com/) - Docker is an open platform for developers and sysadmins to build, ship, and run distributed applications.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags).

## Authors

* **Matthieu AMOROS** - *Initial work* - [SunPaz](https://github.com/SunPaz)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
