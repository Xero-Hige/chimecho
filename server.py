from flask import Flask, render_template

app = Flask(__name__)

from dummy_alert_generator import generate_alerts

groups = {"red": "list-group-item-danger", "green": "list-group-item-success", "blue": "list-group-item-info",
          "yellow": "list-group-item-warning"}


@app.route('/')
def alerts():
    alerts = generate_alerts()
    return render_template("index.html", alerts=alerts, groups=groups)
