from win32com.client import Dispatch  # Used for parsing through Outlook
import time
import os
import datetime
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from backend.MetricGetter.Status_cast import status_cast
# __import__("backend/Metric Getter/Status_cast.status_cast")
from backend.MetricGetter.servicenow import ServiceNow
from backend.MetricGetter.configuration import Configuration
from backend.MetricGetter.Outlook import outlook
from datetime import timedelta, datetime
import getpass



class Metrics:

    config = Configuration("config.yaml")
    my_outlook = outlook() #outlook object
    
    snow_credentials = config.get_credentials()
    # Create an instance of our SNOW API, so we can make requests against it
    service_now = ServiceNow(snow_credentials["url"], snow_credentials["username"], snow_credentials["pass"])

    current_date = datetime.date.today()
    week_ago = current_date - datetime.timedelta(days=7)
    
    #we'll search for these the same as a SNOW "for text" search
    for_text_keys = ["ecc", "solarwinds", "nsg", "log delay"]
    ecc_list = 0
    solarwinds_list = 0
    infosec_list = 0
    nagios_list = 0
    site24x7_list = 0

    #find tickets by caller
    caller_keys = ["Know Be4", "SOC Symantec", "Nagios Integration", "Site 24x7 Service-global"]


    def __init__(self, WeekOf, ECCHostIncidents, Site24x7Incidents, NagiosIncidents, EDIIncidents, 
        InfoSecIncidents, P1Incidents, StatusPageOutages, StatusPagePerformanceDegredations,
        StatusPageMaintenances, CodeChanges, TotalDailiesAlerts, DailiesAffectedServers,
        DailiesRepeatedProblems, SolarWindsIncidents):


        # For grabbing the ECC/Solarwinds Incidents (and maybe some infosec)
        for key in self.for_text_keys:
            tickets = self.service_now.api_get_tickets_in_range(self.week_ago, self.current_date, key)
            if key == "ecc":
                self.ecc_list += 1
            elif key == "solarwinds":
                self.solarwinds_list += 1
            else:
                self.infosec_list += len(tickets['result'])

        # For grabbing Nagios/Site24x7 Incidents
        for key in self.caller_keys:
            tickets = self.service_now.api_get_tickets_in_range(self.week_ago, self.current_date, None, None, key)
            if key == "Nagios Integration":
                self.nagios_list += 1 
            elif key == "Site 24x7 Service-global":
                self.site24x7_list += 1
            else:
                self.infosec_list += len(tickets['result'])


        self.WeekOf = self.week_ago
        self.ECCHostIncidents = self.ecc_list
        self.Site24x7Incidents = self.site24x7_list
        self.NagiosIncidents = self.nagios_list
        #####self.EDIIncidents = EDIIncidents
        self.InfoSecIncidents = self.infosec_list
        self.P1Incidents = self.my_outlook.find_num_outages(self.week_ago, self.current_date)
        #####self.StatusPageOutages = StatusPageOutages
        #####self.StatusPagePerformanceDegredations = StatusPagePerformanceDegredations
        #####self.StatusPageMaintenances = StatusPageMaintenances
        #####self.CodeChanges = CodeChanges
        #####self.TotalDailiesAlerts = TotalDailiesAlerts   
        #####self.DailiesAffectedServers = DailiesAffectedServers
        #####self.DailiesRepeatedProblems = DailiesRepeatedProblems
        self.SolarWindsIncidents = self.solarwinds_list