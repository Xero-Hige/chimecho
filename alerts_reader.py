import csv
import os

ALERTS_PATH = "alerts/"


def load_alerts():
    alerts = []
    for file_name in os.listdir(ALERTS_PATH):
        alerts += read_alerts_file(file_name)

    return alerts


def read_alerts_file(file_name):
    alerts = []
    with open(os.path.join(ALERTS_PATH, file_name)) as my_file:
        reader = csv.reader(my_file)

        for alert in reader:
            alert_type = alert[0].lower()
            alert_name = file_name
            alert_description = alert[1]

            alert_dic = {"TYPE": alert_type, "NAME": alert_name, "DESC": alert_description}
            tags = [alert[i].split("|") for i in range(2, len(alert))]
            alert_dic["TAGS"] = tags
            alerts.append(alert_dic)

    return alerts
