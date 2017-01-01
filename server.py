import csv
import functools
import os
from math import ceil

from flask import Flask, render_template, redirect, url_for, request

from alert_generator import generate_alerts
from alerts_reader import load_alerts, read_alerts_file, list_alerts_types, remove_alert

ALERTS_PER_PAGE = 5
PINED_ALERTS_PER_PAGE = 18

app = Flask(__name__)

groups = {"red": "red", "green": "green", "blue": "blue",
          "yellow": "yellow"}

enabled = {"red": True, "green": True, "yellow": True}


def alert_cmp(alert_1, alert_2):
    if alert_1["TYPE"] == alert_2["TYPE"]:
        if alert_1["NAME"].lower() < alert_2["NAME"].lower():
            return 1
        if alert_1["NAME"] == alert_2["NAME"]:
            return 0
        return -1
    if alert_1["TYPE"].lower() == "red":
        return 1
    if alert_2["TYPE"].lower() == "red":
        return -1
    if alert_1["TYPE"].lower() == "yellow":
        return 1
    return -1


@app.route('/', methods=["GET", "POST"])
def root():
    alerts = load_alerts()
    amounts = {}
    page = int(request.form.get("PAGE", "0"))
    filtered_alerts = []

    added = 0
    for alert in alerts:
        alert_type = alert["TYPE"]
        amount = amounts.get(alert_type, 0) + 1
        amounts[alert_type] = amount
        if not enabled[alert_type]:
            continue
        filtered_alerts.append(alert)
        added += 1

    filtered_alerts.sort(key=functools.cmp_to_key(alert_cmp), reverse=True)

    pages = ceil(len(filtered_alerts) / PINED_ALERTS_PER_PAGE)
    filtered_alerts = [filtered_alerts[i] for i in range(PINED_ALERTS_PER_PAGE * page,
                                                         min(PINED_ALERTS_PER_PAGE * (page + 1), len(filtered_alerts)))]

    return render_template("index.html", pagename="Tablero", alerts=filtered_alerts, groups=groups, amounts=amounts,
                           enabled=enabled, page=page, pages=pages)


@app.route("/load", methods=["GET", "POST"])
def load():
    generate_alerts()
    return redirect(url_for('root'))


@app.route("/list", methods=["GET", "POST"])
def lists():
    alerts_types = list_alerts_types()
    alert_name = request.form.get("ALERT", "")
    page = int(request.form.get("PAGE", "0"))
    alerts = read_alerts_file(alert_name)

    pages = ceil(len(alerts) / ALERTS_PER_PAGE)

    alerts = [alerts[i] for i in range(ALERTS_PER_PAGE * page, min(ALERTS_PER_PAGE * (page + 1), len(alerts)))]

    return render_template("list.html", pagename="Listado completo", alerts=alerts, groups=groups,
                           alerts_types=alerts_types, alert_name=alert_name,
                           page=page, pages=pages)


@app.route("/create", methods=["POST"])
def create_alert_query():
    fields_amount = int(request.form["Fields_Number"])
    query = request.form["Query"]

    querys = []

    names = []
    fields_list = []

    for values in request.form:
        if "FIELD_" in values:
            column_rename = values[6:]
            table_column = request.form[column_rename]
            names.append(table_column)
            fields_list.append(column_rename)

    fields = ", ".join(fields_list) + ", "
    query = query.replace("{FIELDS}", fields)

    for field_id in range(0, fields_amount):
        if "CHK_{0}".format(field_id) in request.form:
            option = request.form.get("{0}_OPTION".format(field_id), "")
            value = request.form.get("{0}_VALUE".format(field_id), "")
            field_query = request.form.get("{0}_QUERY".format(field_id), "")
            if not option or not value or not field_query:
                continue

            field_query = field_query.format(option, value)
            querys.append(field_query)

    query_string = " AND ".join(querys)
    query = query.replace("{CLAUSES}", query_string)

    alert_level = request.form["ALERT_LEVEL"]
    alert_name = request.form["ALERT_NAME"]
    alert_description = request.form["ALERT_DESC"]

    with open("rules/" + alert_name + ".rul", "w") as alert_file:
        alert_file.write(alert_level + "\n")
        alert_file.write(alert_name + "\n")
        alert_file.write(alert_description + "\n")
        alert_file.write(query + "\n")
        alert_file.write(",".join(names) + "\n")

    return redirect(url_for('root'))


@app.route('/delete', methods=["GET", "POST"])
def delete_alerts():
    alerts_types = list_alerts_types()
    return render_template("delete_alerts.html", pagename="Eliminar alertas", alerts_types=alerts_types)


@app.route('/delete_alert', methods=["POST"])
def delete_alert():
    alert_name = request.form.get("ALERT", "")
    remove_alert(alert_name)
    return redirect(url_for('root'))

@app.route('/create')
def create_list():
    templates = []

    for file_name in os.listdir("rules_templates"):
        templates.append(file_name)

    templates.sort()

    return render_template("new_alerts.html", pagename="Templates de alertas", alerts=templates)


@app.route('/create/<template>')
def create(template):
    fields = {}

    path = os.path.join("rules_templates", template)

    if not (os.path.isfile(path)):
        return redirect(url_for('create_list'))

    with open("rules_templates/" + template) as my_file:
        resource_name = my_file.readline()
        reader = csv.reader(my_file)

        for line in reader:
            field_id = int(line[0])

            if field_id == 0:
                fields[field_id] = {"FIELDS": [x.split("|") for x in line[1:]]}
                continue

            elif field_id == -1:
                fields[field_id] = {"QUERY": line[1]}
                continue

            name = line[1]
            field_type = line[2]
            field = {"NAME": name, "TYPE": field_type}

            if field_type == "FREE_COMPARER" or field_type == "CONDITIONAL_COMPARER":
                options_labels = line[3].split("|")
                options_values = line[4].split("|")

                field["OPTIONS"] = [(options_labels[i], options_values[i]) for i in range(len(options_values))]

            if field_type == "CONDITIONAL_COMPARER":
                options_labels = line[5].split("|")
                options_values = line[6].split("|")

                field["VALUES"] = [(options_labels[i], options_values[i]) for i in range(len(options_values))]
                field["VALUES"] = [(options_labels[i], options_values[i]) for i in range(len(options_values))]

            field["QUERY"] = line[-1]
            fields[field_id] = field

    return render_template("generator.html", pagename="Nueva alerta tipo " + template.title(), fields=fields,
                           resource_name=resource_name, sorted=sorted, len=len)


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
