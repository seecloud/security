#!/bin/bash

security-checker &
gunicorn -w 4 -b 0.0.0.0:5000 security.wsgi &

wait -n
