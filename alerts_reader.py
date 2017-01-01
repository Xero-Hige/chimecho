import csv
import os

ALERTS_PATH = "alerts/"


def load_alerts():
    alerts = []
    alerts_files = list_alerts_types()

    for file_name in alerts_files:
        alerts += read_alerts_file(file_name)

    return alerts


def list_alerts_types():
    alerts_files = []
    for file_name in os.listdir(ALERTS_PATH):
        alerts_files.append(file_name)
    alerts_files.sort()
    return alerts_files


def read_alerts_file(file_name):
    alerts = []

    alert_path = os.path.join(ALERTS_PATH, file_name)

    if not os.path.isfile(alert_path):
        return alerts

    with open(alert_path) as my_file:
        reader = csv.reader(my_file)

        for alert in reader:
            if len(alert) < 3:
                continue

            alert_type = alert[0].lower()
            alert_name = file_name
            alert_description = alert[1]

            alert_dic = {"TYPE": alert_type, "NAME": alert_name, "DESC": alert_description}
            tags = [alert[i].split("|") for i in range(2, len(alert))]
            alert_dic["TAGS"] = tags
            alerts.append(alert_dic)

    return alerts
