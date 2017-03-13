from threading import Thread, RLock

import schedule

from alert_generator import generate_alerts_from_rules
from constants_config import *


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
