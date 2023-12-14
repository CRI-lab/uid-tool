#!/bin/bash

npm run tailwind-build
gunicorn -w 4 'app:create_app()'
