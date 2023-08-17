#!/bin/bash

source .venv/bin/activate
tailwindcss -i app/static/src/main.css -o app/static/dist/main.css --watch &
flask run --debug
