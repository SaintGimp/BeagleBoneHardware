#!/bin/bash

if (( $# != 1 ))
then
  echo "Usage: configure-duckdns.sh <token>"
  exit 1
fi

mkdir ~/duckdns
echo "
curl -k \"https://www.duckdns.org/update?domains=saintgimp&token=$1&ip=\"
" >> ~/duckdns/duckdns.sh

chmod +x ~/duckdns/duckdns.sh

line="*/15 * * * * /home/elee/duckdns/duckdns.sh >/dev/null 2>&1"
(crontab -u elee -l; echo "$line" ) | crontab -u elee -