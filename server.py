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

    def get_enabled_alerts(self):
        return self.enabled_alerts

    def get_groups(self):
        return self.groups

    def get_alerts_types_counts(self):
        return self.alerts_types_counts

    def set_alerts_types_counts(self, counts):
        self.alerts_types_counts = counts
        self.updated_type_counts = True

    def get_alerts_counts(self):
        return self.alerts_counts

    def set_alerts_counts(self, counts):
        self.alerts_counts = counts
        self.updated_counts = True

    def reset_alerts_count(self):
        self.alerts_counts = 0
        self.updated_counts = False

    def reset_alerts_types_counts(self):
        self.alerts_types_counts = {}
        self.updated_type_counts = False

    def are_counts_updated(self):
        return self.updated_counts

    def are_types_counts_updated(self):
        return self.updated_type_counts

    def is_server_updated(self):
        return self.updated_type_counts and self.updated_counts

    def toggle_alert(self, alert_type):
        if alert_type not in self.__ALERT_TYPES:
            return

        self.enabled_alerts[alert_type] = not self.enabled_alerts[alert_type]
