import csv

from flask import Flask, render_template, redirect, url_for, request

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


@app.route("/create", methods=["POST"])
def soldfor():
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
        alert_file.write(alert_level+"\n")
        alert_file.write(alert_name+"\n")
        alert_file.write(alert_description+"\n")
        alert_file.write(query+"\n")
        alert_file.write(",".join(names)+"\n")

    return redirect(url_for('root'))


@app.route('/quest')
def create():
    fields = {}
    with open("classes") as my_file:
        resource_name = my_file.readline()
        reader = csv.reader(my_file)

        for line in reader:
            id = int(line[0])

            if id == 0:
                fields[id] = {"FIELDS": [x.split("|") for x in line[1:]]}
                continue

            elif id == -1:
                fields[id] = {"QUERY": line[1]}
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
            fields[id] = field

    return render_template("generator.html", fields=fields, resource_name=resource_name, sorted=sorted, len=len)


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
