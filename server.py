from flask import Flask, render_template
app = Flask(__name__)

import alert_generator

@app.route('/')
def alerts():
    alerts = alert_generator.generate_alerts()
    return render_template("index.html",alerts=alerts)
