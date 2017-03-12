import csv
import os
from math import ceil

from flask import Flask, render_template, redirect, url_for, request

from alert_generator import generate_alerts_from_rules
from alerts_reader import load_enabled_alerts, read_alerts_file, list_alerts_types, remove_alert
from constants_config import *
from server import Server

app = Flask(__name__)

server = Server()


@app.route('/', methods=["GET", "POST"])
def root():
    page = int(request.form.get("PAGE", "0"))

    alerts, alerts_amount, types_amounts = load_enabled_alerts(enabled_alerts_dic=server.get_enabled_alerts(),
                                                               offset=PINED_ALERTS_PER_PAGE * page,
                                                               window_size=PINED_ALERTS_PER_PAGE,
                                                               acumulate=not server.is_server_updated())

    if not server.are_counts_updated():
        server.set_alerts_counts(alerts_amount)

    if not server.are_types_counts_updated():
        server.set_alerts_types_counts(types_amounts)

    pages = ceil(server.get_alerts_counts() / PINED_ALERTS_PER_PAGE)

    return render_template("index.html",
                           pagename="Tablero",
                           alerts=alerts,
                           groups=server.get_groups(),
                           amounts=server.get_alerts_types_counts(),
                           enabled=server.get_enabled_alerts(),
                           page=page,
                           pages=pages)


@app.route("/load", methods=["GET", "POST"])
def load():
    generate_alerts_from_rules()
    server.reset_alerts_count()
    server.reset_alerts_types_counts()
    return redirect(url_for('root'))


@app.route("/list", methods=["GET", "POST"])
def lists():
    alerts_types = list_alerts_types()
    alert_name = request.form.get("ALERT", "")

    if alert_name:
        alerts = read_alerts_file(alert_name)[0]
    else:
        alerts = []

    page = int(request.form.get("PAGE", "0"))
    pages = ceil(len(alerts) / ALERTS_PER_PAGE)

    alerts = [alerts[i] for i in range(ALERTS_PER_PAGE * page, min(ALERTS_PER_PAGE * (page + 1), len(alerts)))]

    return render_template("list.html",
                           pagename="Listado completo",
                           alerts=alerts,
                           groups=server.get_groups(),
                           alerts_types=alerts_types,
                           alert_name=alert_name,
                           page=page,
                           pages=pages)


@app.route("/create", methods=["POST"])
def create_alert_query():
    fields_amount = int(request.form["Fields_Number"])
    query = request.form["Query"]

    names = []
    fields_list = []
    agregate_list = []

    for values in request.form:
        if "FIELD_" in values:
            column_rename = values[6:]
            table_column = request.form[column_rename]
            names.append(table_column)
            if "(" in column_rename:
                agregate_list.append(column_rename)
            else:
                fields_list.append(column_rename)

    fields = ", ".join(fields_list) + ", "
    query = query.replace("{FIELDS_COMMON}", fields)

    fields = ", ".join(agregate_list) + ", "
    query = query.replace("{FIELDS_AGREGATE}", fields)

    where_fields = []
    having_fields = []

    for field_id in range(0, fields_amount):
        if "CHK_{0}".format(field_id) in request.form:
            option = request.form.get("{0}_OPTION".format(field_id), "")
            value = "'" + request.form.get("{0}_VALUE".format(field_id), "") + "'"  # Ads quotes to values
            field_query = request.form.get("{0}_QUERY".format(field_id), "")
            if not option or not value or not field_query:
                continue

            field_query = field_query.format(option, value)

            if request.form.get("{0}_IS_AGREGATE".format(field_id), ""):
                having_fields.append(field_query)
            else:
                where_fields.append(field_query)

    if where_fields:
        query_string = "WHERE " + " AND ".join(where_fields)
        query = query.replace("{WHERE_CLAUSES}", query_string)

    if having_fields:
        query_string = "HAVING " + " AND ".join(having_fields)
        query = query.replace("{HAVING_CLAUSES}", query_string)

    query = query.replace("{ORDER_FIELD}", "")

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
    return render_template("delete_alerts.html",
                           pagename="Eliminar alertas",
                           alerts_types=alerts_types)


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

    return render_template("new_alerts.html",
                           pagename="Templates de alertas",
                           alerts=templates)


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

            field = {"NAME": name, "TYPE": field_type, "AGREGATE": False}

            if field_type == FIELD_FREE_COMPARER or field_type == FIELD_CONDITIONAL_COMPARER:
                options_labels = line[3].split("|")
                options_values = line[4].split("|")

                field["OPTIONS"] = [(options_labels[i], options_values[i]) for i in range(len(options_values))]

            if field_type == FIELD_CONDITIONAL_COMPARER:
                options_labels = line[5].split("|")
                options_values = line[6].split("|")

                field["VALUES"] = [(options_labels[i], options_values[i]) for i in range(len(options_values))]
                field["VALUES"] = [(options_labels[i], options_values[i]) for i in range(len(options_values))]

            field["QUERY"] = line[-1]

            if "(" in field["QUERY"]:
                field["AGREGATE"] = True

            fields[field_id] = field

    return render_template("generator.html",
                           pagename="Nueva alerta tipo " + template.title(),
                           fields=fields,
                           resource_name=resource_name,
                           sorted=sorted,
                           len=len)


@app.route('/toggleRed')  # TODO: IMPROVE
def toggle_red():
    server.toggle_alert(ALERT_RED)
    server.reset_alerts_count()
    return redirect(url_for('root'))


@app.route('/toggleGreen')
def toggle_green():
    server.toggle_alert(ALERT_GREEN)
    server.reset_alerts_count()
    return redirect(url_for('root'))


@app.route('/toggleYellow')
def toggle_yellow():
    server.toggle_alert(ALERT_YELLOW)
    server.reset_alerts_count()
    return redirect(url_for('root'))
