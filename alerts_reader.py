import csv
import os

from constants_config import *


def load_alerts():
    alerts = []
    alerts_files = list_alerts_types()

    for filename in alerts_files:
        alerts += read_alerts_file(filename)

    return alerts


def list_alerts_types():
    alerts_files = []
    for filename in os.listdir(ALERTS_DIR):
        alerts_files.append(filename)
    alerts_files.sort()
    return alerts_files


def read_alerts_file(filename):
    alerts = []

    alert_path = os.path.join(ALERTS_DIR, filename)

    if not os.path.isfile(alert_path):
        return alerts

    with open(alert_path) as my_file:
        reader = csv.reader(my_file)

        for alert in reader:
            if len(alert) < 3:
                continue

            alert_type = alert[0].lower()
            alert_name = filename
            alert_description = alert[1]

            alert_dic = {"TYPE": alert_type, "NAME": alert_name, "DESC": alert_description}
            tags = [alert[i].split("|") for i in range(2, len(alert))]
            alert_dic["TAGS"] = tags
            alerts.append(alert_dic)

    return alerts


def remove_alert(filename):
    alert_path = os.path.join(ALERTS_DIR, filename)
    os.remove(alert_path)
    alert_path = os.path.join(RULES_DIR, filename + ".rul")
    os.remove(alert_path)
