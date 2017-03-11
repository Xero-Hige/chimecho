import csv
import functools
import os
import shutil


# con = cx_Oracle.connect('CONECTION')


def generate_alerts():
    for file_name in os.listdir("rules/"):
        generate_alert_file(file_name)


def generate_alert_file(rules_filename):
    alerts = []
    with open("rules/" + rules_filename) as my_file:
        alert_type = my_file.readline().rstrip()
        alert_name = my_file.readline().rstrip()
        alert_description = my_file.readline().rstrip()
        alert_query = my_file.readline().rstrip()
        alert_results_tags = my_file.readline().rstrip().split(",")

        # cur = con.cursor()
        # cur.execute(alert_query)
        cur = [("115", "13"), ("99", "192"), ("74", "88")]
        for result in cur:
            alert = generate_alert(alert_description, alert_name, alert_results_tags, alert_type, result)
            alerts.append(alert)
            # cur.close()
    rules_filename = rules_filename.replace(".rul", "")
    with open("alerts/" + rules_filename, 'w') as my_file:
        writer = csv.writer(my_file)
        for alert in alerts:
            line = [alert["TYPE"], alert["DESC"]]
            for tag in alert["TAGS"]:
                line.append("|".join(tag))
            writer.writerow(line)


def generate_alert(alert_description, alert_name, alert_results_tags, alert_type, result):
    alert = {"TYPE": alert_type, "NAME": alert_name, "DESC": alert_description}
    tags = [(alert_results_tags[i], result[i]) for i in range(len(alert_results_tags))]
    alert["TAGS"] = tags
    return alert


def csv_next(csv_reader):
    try:
        return csv_reader.next()
    except StopIteration:
        return []


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


def merge_alerts_files(alerts1_filename, alerts2_filename):
    """Takes 2 alerts filenames and merges both registries in a new file. Returns the new filename"""
    with open(alerts1_filename) as input1:
        with open(alerts2_filename) as input2:
            with open("temporal_merge.tmp") as temp_output:
                reader1 = csv.reader(input1)
                reader2 = csv.reader(input2)
                writer = csv.writer(temp_output)

                create_ordered_alert_list(reader1, reader2, writer)

    shutil.copyfile("temporal_merge.tmp", "SortedAlerts")
    return "SortedAlerts"


def create_ordered_alert_list(reader1, reader2, writer):
    """Merges two open csv alerts files in the writer.
        The input files must be ordered"""

    alert1 = csv_next(reader1)
    alert2 = csv_next(reader2)
    while alert1 and alert2:
        if alert1 <= alert2:
            writer.writerow(alert1)
            alert1 = csv_next(reader1)
            continue
        writer.writerow(alert2)
        alert2 = csv_next(reader2)
    for alert in reader1:
        writer.writerow(alert)
    for alert in reader2:
        writer.writerow(alert)


def sort_alerts():
    alerts = []
    for filename in os.listdir("./alerts"):
        alerts.append(os.path.join("./alerts", filename))
    functools.reduce(merge_alerts_files, alerts)
