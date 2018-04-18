# Access-Ctrl-HID

An access controller based on HID card technology and Raspberry PI

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Installing

On your raspberry Pi board :
Python / Packet Manager (pip) and main packages (RPi.GPIO
```
git clone http://github.com/SunPaz/access-ctrl-hid
cd _deploy
chmod 740 delpoy_requiered_modules.sh
sh delpoy_requiered_modules.sh
```
## Running the tests

To check installation, you can run

```
cd _deploy
python test_python_packages.py
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Flask](http://flask.pocoo.org/docs/0.12/) - Flask is a micro webdevelopment framework for Python.
* [RPi.GPIO](https://pypi.org/project/RPi.GPIO/) - Provides a class to control the GPIO on a Raspberry Pi.
* [MFRC522](https://github.com/pimylifeup/MFRC522-python) - MFRC522 Wrapper

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Matthieu AMOROS** - *Initial work* - [SunPaz](https://github.com/SunPaz)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
