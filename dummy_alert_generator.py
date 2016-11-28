import os
from random import randint, choice  # import cx_Oracle


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
            cur = [[randint(0, 500) for x in range(len(alert_results_tags))] for i in range(randint(15, 30))]
            for result in cur:
                alert = {}
                alert["TYPE"] = choice(["red", "green", "blue", "yellow"])  # alert_type
                alert["NAME"] = alert_name
                alert["DESC"] = alert_description
                tags = [(alert_results_tags[i], result[i]) for i in range(len(result))]
                alert["TAGS"] = tags
                alerts.append(alert)
                # cur.close()
    return alerts
