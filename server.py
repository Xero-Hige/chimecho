from flask import Flask, render_template
app = Flask(__name__)

import daemon

@app.route('/')
def alerts():
    alerts = daemon.run() #FIXME: Rename
    return render_template("index.html",alerts=alerts)
