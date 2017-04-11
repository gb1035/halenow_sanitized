#Halenow#

This project is a queue managment system for John Hale written in Tornado. This uses either Twilio, or textbelt to send text messages.

## Getting this repo ##
```bash
git clone git@github.com:gb1035/halenow.git
git checkout tornado
exit
```

## Install Requirements ##
It is necessary to install dependencies in order to test the site locally before pushing to deployment.

### Linux ###
```bash
cat apt-requirements | xargs sudo apt-get install
sudo pip install -r requirements
```

### Mac ###
```bash
cat brew-requirements | xargs brew install
sudo pip install -r requirements
```
## Install Requirements ##
In order to run this, you need to create the setup file.
``` bash
cp example_settings.py settings.py
```
Then you need to fill out the following:
* CAPTCHA_SECRET = the secret key from google.com/recaptcha/
* BASEDIR = the directory of the program
* DB settings = database settings. The program will create DB_USER during setup
(The admin user must be able to create databases, tables, and users)
* TORNADO_SECRET = a random string to be used by tornado for secret.
* ADMIN_KEY = The password for the admin login
* USE_TWILLIO = If true, use Twilio, else use textbelt

### If you wish to use https ###
``` bash
mkdir cert_files
ln -s <path to cert> server.crt
ln -s <path to key> server.key
``` 
Or you can change the CERTFILE and KEYFILE settings.

## First Time Setup ##
In order to set up the db, spmply run
``` bash
python app -setup
```
once. There should be no output and it will exit once it is done.

## Building the site and running ##
To run the site:
```bash
python app
```

Now go to: [http://127.0.0.1:8080/](http://127.0.0.1:8080/)
or what you set the port to.

And you should see the site.

When you make changes to the site, it will automaticaly rebuild as long as it is serving.
