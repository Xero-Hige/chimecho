import os
from random import randint, choice, shuffle  # import cx_Oracle


# con = cx_Oracle.connect('CONECTION')

def generate_alerts():
    alerts = []
    for file_name in os.listdir("rules/"):
        with open("rules/" + file_name) as my_file:
            alert_type = my_file.readline().rstrip()
            alert_name = my_file.readline().rstrip()
            alert_description = my_file.readline().rstrip()
            alert_query = my_file.readline().rstrip()
            alert_results_tags = my_file.readline().rstrip().split(",")

            # cur = con.cursor()
            # cur.execute(alert_query)
            cur = [[randint(0, 500) for x in range(len(alert_results_tags))] for i in range(25)]
            for result in cur:
                alert = {"TYPE": alert_type, "NAME": alert_name, "DESC": alert_description,
                         "TAGS": [(alert_results_tags[i], result[i]) for i in range(len(result))]}

                alerts.append(alert)
                # cur.close()
    shuffle(alerts)
    return alerts
