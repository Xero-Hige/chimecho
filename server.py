from flask import Flask, render_template, redirect, url_for
from dummy_alert_generator import generate_alerts

app = Flask(__name__)

groups = {"red": "list-group-item-danger", "green": "list-group-item-success", "blue": "list-group-item-info",
          "yellow": "list-group-item-warning"}

enabled = {"red": True, "green": True, "yellow": True}


@app.route('/')
@app.route('/index')
def root():
    alerts = generate_alerts()
    amounts = {}

    filtered_alerts = []

    for alert in alerts:
        type = alert["TYPE"]
        amount = amounts.get(type, 0) + 1
        amounts[type] = amount
        if not enabled[type]:
            continue
        filtered_alerts.append(alert)

    return render_template("index.html", alerts=filtered_alerts, groups=groups, amounts=amounts,
                           enabled=enabled)


@app.route('/toggleRed')
def toggle_red():
    enabled["red"] = not enabled["red"]
    return redirect(url_for('root'))


@app.route('/toggleGreen')
def toggle_green():
    enabled["green"] = not enabled["green"]
    return redirect(url_for('root'))


@app.route('/toggleYellow')
def toggle_yellow():
    enabled["yellow"] = not enabled["yellow"]
    return redirect(url_for('root'))
