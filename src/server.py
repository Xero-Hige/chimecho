from threading import Thread, RLock

import schedule

from alert_generator import generate_alerts_from_rules
from alerts_reader import load_enabled_alerts
from constants_config import *


def is_date(date_string):
    date_list = date_string.split("-")
    if len(date_list) != 3:
        return False

    return len(date_list[0]) == 4 and len(date_list[1]) == 2 and len(date_list[2]) == 2 and date_list[0].isdigit() and \
           date_list[1].isdigit() and date_list[2].isdigit()


class Server(object):
    __ALERT_TYPES = [ALERT_RED, ALERT_GREEN, ALERT_YELLOW]

    def __init__(self):
        self.enabled_alerts = {alert: True for alert in self.__ALERT_TYPES}
        self.groups = {alert: alert for alert in self.__ALERT_TYPES}
        self.alerts_counts = 0
        self.alerts_types_counts = {}

        self.updated_counts = False
        self.updated_type_counts = False

        self.updating = False
        self.server_status_lock = RLock()

        self.reload_alerts()
        load_enabled_alerts(enabled_alerts_dic=self.get_enabled_alerts())

        schedule.every().day.at("01:40").do(self.reload_alerts)

    def get_enabled_alerts(self):
        return self.enabled_alerts

    def get_groups(self):
        return self.groups

    def get_alerts_types_counts(self):
        return self.alerts_types_counts

    def set_alerts_types_counts(self, counts):
        self.server_status_lock.acquire()

        if self.updating:
            self.server_status_lock.release()
            return

        self.alerts_types_counts = counts
        self.updated_type_counts = True

        self.server_status_lock.release()

    def get_alerts_counts(self):
        return self.alerts_counts

    def set_alerts_counts(self, counts):
        self.server_status_lock.acquire()

        if self.updating:
            self.server_status_lock.release()
            return

        self.alerts_counts = counts
        self.updated_counts = True

        self.server_status_lock.release()

    def reset_alerts_count(self):
        self.server_status_lock.acquire()

        if self.updating:
            self.server_status_lock.release()
            return

        self.alerts_counts = 0
        self.updated_counts = False

        self.server_status_lock.release()

    def reset_alerts_types_counts(self):
        self.server_status_lock.acquire()

        if self.updating:
            self.server_status_lock.release()
            return

        self.alerts_types_counts = {}
        self.updated_type_counts = False

        self.server_status_lock.release()

    def are_counts_updated(self):
        return self.updated_counts

    def are_types_counts_updated(self):
        return self.updated_type_counts

    def is_server_updated(self):
        self.server_status_lock.acquire()
        status = self.updated_type_counts and self.updated_counts
        self.server_status_lock.release()
        return status

    def toggle_alert(self, alert_type):
        if alert_type not in self.__ALERT_TYPES:
            return

        self.enabled_alerts[alert_type] = not self.enabled_alerts[alert_type]

    def reload_alerts(self):

        self.server_status_lock.acquire()
        if self.updating:
            self.server_status_lock.release()
            return

        self.updating = True
        self.server_status_lock.release()

        reloader_thread = Thread(target=self.__reload_alerts)
        reloader_thread.start()

    def __reload_alerts(self):
        generate_alerts_from_rules()

        self.server_status_lock.acquire()

        self.updating = False
        self.reset_alerts_count()
        self.reset_alerts_types_counts()

        self.server_status_lock.release()
