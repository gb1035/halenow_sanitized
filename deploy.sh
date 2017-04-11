#!/bin/bash

apt-get update
apt-get upgrade -y
cat apt-requirements | xargs apt-get install -y 

pip install -r requirements.txt

mysql_secure_installation

#Note, only works on upstart based systems.
cp webserver.conf /etc/init/webserver.conf

initctl start webserver.conf
