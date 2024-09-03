# AstrophotoWebStack
A web interface for astrophoto stacking

.env file:
```bash
SECRET_KEY=123ada
HOME_DIR=/mnt/astrotmp/
SIRIL_CLI=/usr/bin/siril-cli
```

The home dir is the directory where the individual project folders are to be stored. The current type of folder organization supported is:

ROOT_DIR
- PROJECT_NAME
  - LIGHTS
    - LIGHT1.fit
    - ...
    - LIGHTN.fit
  - DARKS
    - DARK1.fit
    - ...
    - DARKN.fit
  - FLATS
    - FLAT1.fit
    - ...
    - FLATN.fit
  - BIAS
    - BIAS1.fit
    - ...
    - BIASN.fit
  - MASTERS
    - MASTER_FLAT.fit
    - MASTER_BIAS.fit
    - MASTER_DARK.fit
- PROJECT_NAME2
  - ...
- PROJECT_NAMEN

The folder name does not matter, it is selected in the APWebUI. The masters are to be stored in a separate folder, in order to be used (and selected).

Currently, .xisf images are not supported, will be added in a future version (hopefully).

## Installation (APWebUI)
```bash
pip install pipenv
pipenv install
pipenv --venv
> /home/user/.local/share/virtualenvs/AstrophotoWebStack-xxxxxx
```

now update `scripts/app.wsgi` with the path to the virtualenv.

## Apache configuration
```xml
<VirtualHost *:80>
	ServerName 192.168.0.1

	WSGIDaemonProcess flaskapp user=stacker group=stacker threads=5
	WSGIScriptAlias / /var/www/AstrophotoWebStack/scripts/app.wsgi

	<Directory /var/www/AstrophotoWebStack>
			WSGIProcessGroup flaskapp
			WSGIApplicationGroup %{GLOBAL}
			Order deny,allow
			Allow from all
	</Directory>

	ErrorLog ${APACHE_LOG_DIR}/apstack_error.log
	CustomLog ${APACHE_LOG_DIR}/apstack_access.log combined
</VirtualHost>
```

use the correct IP address and path to the app.wsgi file.

## Installation (stacker)

Install pysiril from [wheel](https://gitlab.com/free-astro/pysiril/-/releases):
```bash
pip install pysiril-0.0.15-py3-none-any.whl
```

Install siril executable:
```bash
sudo add-apt-repository ppa:lock042/siril
sudo apt-get update
sudo apt-get install siril
```

(newer version, on normal apt there is an older version)

Now you can run the stacker.py script or automate it with cron (run it automatically every x minutes when it is not already running).