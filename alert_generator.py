import os

import cx_Oracle

con = cx_Oracle.connect('CONECTION')


def generate_alerts():
    alerts = []
    for file_name in os.listdir("rules/"):
        with open("rules/" + file_name) as my_file:
            alert_type = my_file.readline().rstrip()
            alert_name = my_file.readline().rstrip()
            alert_description = my_file.readline().rstrip()
            alert_query = my_file.readline().rstrip()
            alert_results_tags = my_file.readline().rstrip().split(",")

            cur = con.cursor()
            cur.execute(alert_query)
            # cur = [(12,13),(15,192),(8,88)]
            for result in cur:
                alert = {"TYPE": alert_type, "NAME": alert_name, "DESC": alert_description}
                tags = [(alert_results_tags[i], result[i]) for i in range(len(result))]
                alert["TAGS"] = tags
                alerts.append(alert)
            cur.close()
    return alerts
