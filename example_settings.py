import os

#Tornado settings
STATIC_PATH = os.path.join(os.path.dirname(__file__), "static")
TORNADO_SECRET = 'place_random_string_here'
XSRF_COOKIES = False


root = os.path.dirname(__file__)
template_root = os.path.join(root, 'templates')
blacklist_templates = ('layouts',)
BASEDIR = 'place_path_here' #This is the full path of the project's location.

#DB settings, this user will be created and granted permissions.
DB_USER_USER = 'db_user'
DB_USER_PASS = 'db_pass'

#HTTP Settings
HTTPS = False
HTTPS_PORT = 8443
HTTP_PORT = 8080
CERTFILE = BASEDIR + "cert_files/server.crt"
KEYFILE = BASEDIR + "cert_files/server.key"

#Login settings
ADMIN_KEY = 'admin_key_here'
API_KEY = 'replace_with_random_string'

#jinja2 settings
JINJA2_SETTINGS = {
    'sidenav':False,
   'navbar':True,
}

#Arrow settings
HUMANIZE = True #If false, will use exact time settings below
DATE_FORMAT = 'YYYY-MM-DD HH:mm:ss'
TIMEZONE = 'US/Central'

#Number settings
MAX_NUMBER = 100 #inclusive

#Twilio settings:
SEND_TEXTS = True
USE_TWILLIO = False
TWILIO_ACCOUNT_SID = "insert_value_here" # Your Account SID from www.twilio.com/console
TWILIO_AUTH_TOKEN  = "insert_value_here"  # Your Auth Token from www.twilio.com/console
TWILIO_FROM_NUMB = '+1phone_here '
TEXT_MESSAGE = "Hale will see you now"

#Users settings:
USE_BCRYPT = True
