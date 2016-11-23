import os
import cx_Oracle

#con = cx_Oracle.connect('owner_rafam/ownerdba@154.2.6.107:1521/MEZEIZA')

def run():
    for file_name in os.listdir("rules/"):
        with open("rules/"+file_name) as my_file:
            alert_type = my_file.readline().rstrip()
            alert_query = my_file.readline().rstrip()
            alert_results_tags = my_file.readline().rstrip().split(",")

            #cur = con.cursor()
            #cur.execute(alert_query)
            cur = [(12,13),(15,192),(8,88)]
            for result in cur:
                print("Alert: "+alert_type)
                for i in range(len(alert_results_tags)):
                    print("\t"+alert_results_tags[i]+" : "+str(result[i]))

            #cur.close()

run()
