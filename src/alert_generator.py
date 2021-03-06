import csv
import functools
import logging
import os
import shutil

import cx_Oracle

from connection import *
from constants_config import *


def alert_cmp(alert_1, alert_2):
    """Compares 2 alerts represented as lists"""
    if alert_1[ALERT_TYPE_FIELD] == alert_2[ALERT_TYPE_FIELD]:
        if alert_1[ALERT_NAME_FIELD].lower() < alert_2[ALERT_NAME_FIELD].lower():
            return 1
        if alert_1[ALERT_NAME_FIELD] == alert_2[ALERT_NAME_FIELD]:
            return 0
        return -1
    if alert_1[ALERT_TYPE_FIELD].lower() == ALERT_RED:
        return 1
    if alert_2[ALERT_TYPE_FIELD].lower() == ALERT_RED:
        return -1
    if alert_1[ALERT_TYPE_FIELD].lower() == ALERT_YELLOW:
        return 1
    return -1


def __merge_ordered_alert_list(reader1, reader2, writer):
    """Merges two open csv alerts files in the writer.
        The input files must be ordered"""

    alert1 = next(reader1, "")
    alert2 = next(reader2, "")
    while alert1 and alert2:
        if alert1 <= alert2:
            writer.writerow(alert1)
            alert1 = next(reader1, "")
            continue
        writer.writerow(alert2)
        alert2 = next(reader2, "")
    for alert in reader1:
        writer.writerow(alert)
    for alert in reader2:
        writer.writerow(alert)


def __merge_alerts_files(alerts1_filename, alerts2_filename):
    """Takes 2 alerts filenames and merges both registries in a new file. Returns the new filename"""
    with open(alerts1_filename) as input1:
        with open(alerts2_filename) as input2:
            with open("temporal_merge.tmp", "w") as temp_output:
                reader1 = csv.reader(input1)
                reader2 = csv.reader(input2)
                writer = csv.writer(temp_output)

                __merge_ordered_alert_list(reader1, reader2, writer)

    shutil.copyfile("temporal_merge.tmp", ALL_ALERTS_FILE)
    return ALL_ALERTS_FILE


def __generate_sorted_alerts_file():
    alerts = []
    for filename in os.listdir(ALERTS_DIR):
        alerts.append(os.path.join(ALERTS_DIR, filename))

    if not alerts:
        return

    alerts.append("/dev/null")
    functools.reduce(__merge_alerts_files, alerts)


def __generate_alert(alert_description, alert_name, alert_results_tags, alert_type, result):
    alert = {ALERT_TYPE_FIELD: alert_type, ALERT_NAME_FIELD: alert_name, ALERT_DESCRIPTION_FIELD: alert_description}
    tags = [(alert_results_tags[i], result[i]) for i in range(len(alert_results_tags))]
    alert[ALERT_TAGS_FIELD] = tags
    return alert


def __generate_alert_file(rules_filename):
    con = cx_Oracle.connect(BD_STRING)

    alerts = []
    with open(os.path.join(RULES_DIR, rules_filename)) as my_file:
        alert_type = my_file.readline().rstrip().upper()
        alert_name = my_file.readline().rstrip().capitalize()
        alert_description = my_file.readline().rstrip()
        alert_query = my_file.readline().rstrip()
        alert_results_tags = my_file.readline().rstrip().split(",")

        cur = con.cursor()
        logging.warning("Executing query: " + str(alert_query))

        try:
            cur.execute(alert_query)
        except cx_Oracle.DatabaseError as e:
            logging.warning("Non executed: {0}".format(e))
            return

        for result in cur:
            alert = __generate_alert(alert_description, alert_name, alert_results_tags, alert_type, result)
            alerts.append(alert)

    con.close()
    alert_filename = rules_filename.replace(RULES_FILE_EXTENSION, ALERTS_FILE_EXTENSION)

    with open(os.path.join(ALERTS_DIR, alert_filename), 'w') as my_file:
        writer = csv.writer(my_file)
        logging.warning("Opened")
        for alert in alerts:
            line = [alert[ALERT_TYPE_FIELD], alert[ALERT_NAME_FIELD], alert[ALERT_DESCRIPTION_FIELD]]
            for tag in alert[ALERT_TAGS_FIELD]:
                line.append("|".join((str(tag[0]),str(tag[1]))))
            writer.writerow(line)

def generate_alerts_from_rules():
    for file_name in os.listdir(RULES_DIR):
        __generate_alert_file(file_name)
    __generate_sorted_alerts_file()
