import os

# import cx_Oracle
import csv


# con = cx_Oracle.connect('CONECTION')


def generate_alerts():
    for file_name in os.listdir("rules/"):
        alerts = []
        with open("rules/" + file_name) as my_file:
            alert_type = my_file.readline().rstrip()
            alert_name = my_file.readline().rstrip()
            alert_description = my_file.readline().rstrip()
            alert_query = my_file.readline().rstrip()
            alert_results_tags = my_file.readline().rstrip().split(",")

            # cur = con.cursor()
            # cur.execute(alert_query)
            cur = [("115", "13"), ("99", "192"), ("74", "88")]
            for result in cur:
                alert = {"TYPE": alert_type, "NAME": alert_name, "DESC": alert_description}
                tags = [(alert_results_tags[i], result[i]) for i in range(len(alert_results_tags))]
                alert["TAGS"] = tags
                alerts.append(alert)
                # cur.close()
        file_name = file_name.replace(".rul", "")
        with open("alerts/" + file_name, 'w') as my_file:
            writer = csv.writer(my_file)
            for alert in alerts:
                line = [alert["TYPE"], alert["DESC"]]
                for tag in alert["TAGS"]:
                    line.append("|".join(tag))
                writer.writerow(line)
