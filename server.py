from flask import Flask, render_template , redirect, url_for

app = Flask(__name__)

from dummy_alert_generator import generate_alerts

groups = {"red": "list-group-item-danger", "green": "list-group-item-success", "blue": "list-group-item-info",
          "yellow": "list-group-item-warning"}

enabled = {"red": False, "green": True, "yellow": True}


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
def toggleRed():
    enabled["red"] = not enabled["red"]
    return redirect(url_for('root'))

@app.route('/toggleGreen')
def toggleGreen():
    enabled["green"] = not enabled["green"]
    return redirect(url_for('root'))

@app.route('/toggleYellow')
def toggleYellow():
    enabled["yellow"] = not enabled["yellow"]
    return redirect(url_for('root'))