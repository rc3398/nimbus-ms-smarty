# COMS6156 Nimbus
Columbia University \
Fall 2022 COMS6156 - Cloud Compute \
Professor Donald F Ferguson \
Project Nimbus

## Local setup

### Requirements
* Python 3.9 or higher
* MacOS/Linux

To build the service locally, create a Python venv, then clone the repository.

```sh
python3 -m venv env-path
cd env-path
source bin/activate
git clone https://github.com/rc3398/nimbus-ms-smarty.git
```

Next you'll want to enter the repository directory and install the requirements. \

```sh
cd nimbus-ms-smarty
python3 -m pip3 install --upgrade pip3
```

NOTE: It is advisable you run this command every time you do a pull.
```sh
pip3 install -r requirements.txt
```
### Running the Flask REST API locally
```sh
cd nimbus-ms-smarty/web-app
python3 app.py
```
