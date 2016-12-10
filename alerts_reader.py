import os
import csv


def load_alerts():
    alerts = []
    for file_name in os.listdir("alerts/"):
        with open("alerts/" + file_name) as my_file:

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
