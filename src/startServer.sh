#!/usr/bin/env bash
export LANG=C.UTF-8
export LC_ALL=C.UTF-8
export FLASK_APP=server_frontend.py
touch allAlerts.db
flask run
