import csv
import os

from constants_config import *


def load_enabled_alerts(enabled_alerts_dic):
    types_acumulator = {ALERT_RED: 0}
    alerts = read_alerts_file(ALL_ALERTS_FILE, enabled_alerts_dic, "", types_acumulator)
    return len(alerts), alerts, types_acumulator


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


def read_alerts_file(filename, filter_dic=None, base_dir=ALERTS_DIR, type_acumulator=None):
    alerts = []

    alert_path = os.path.join(base_dir, filename)

    if not os.path.isfile(alert_path):
        return alerts

    with open(alert_path) as my_file:
        reader = csv.reader(my_file)

        for alert in reader:
            if len(alert) < ALERT_TAGS_INDEX + 1:  # No enough fields
                continue

            alert_type = alert[ALERT_TYPE_INDEX].lower()

            if filter_dic:
                if alert_type not in filter_dic or not filter_dic[alert_type]:
                    continue

            if type_acumulator:
                type_acumulator[alert_type] = type_acumulator.get(alert_type, 0) + 1

            alert_name = alert[ALERT_NAME_INDEX]
            alert_description = alert[ALERT_DESCRIPTION_INDEX]

            alert_dic = {ALERT_TYPE_FIELD: alert_type,
                         ALERT_NAME_FIELD: alert_name,
                         ALERT_DESCRIPTION_FIELD: alert_description}
            tags = [alert[i].split("|") for i in range(ALERT_TAGS_INDEX, len(alert))]
            alert_dic[ALERT_TAGS_FIELD] = tags

            alerts.append(alert_dic)

    return alerts


def remove_alert(filename):
    alert_path = os.path.join(ALERTS_DIR, filename)
    os.remove(alert_path)
    alert_path = os.path.join(RULES_DIR, filename + RULES_FILE_EXTENSION)
    os.remove(alert_path)
