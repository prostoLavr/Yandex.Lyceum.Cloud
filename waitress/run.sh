#!/usr/bin/bash
waitress-serve --host="0.0.0.0" --port=5000 --max-request-body-size=10737418242 --max-request-header-size=5242880 wsgi:app 
