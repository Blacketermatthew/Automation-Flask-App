from sqlalchemy.sql.sqltypes import Time
# from lib.aniso8601 import date
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
# from application.routes import PSQ
from . import app
from datetime import datetime, date, timedelta
from dotenv import load_dotenv
import os
import sys
import requests
import openpyxl
import xlsxwriter
import csv



db = SQLAlchemy(app)



class User(db.Model):
    __tablename__ = "users"
    
    user_id     =   db.Column(db.Integer, primary_key=True)
    username    =   db.Column(db.String(50), unique=True, nullable=False)
    password    =   db.Column(db.String(50), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return self.username


class WeeklyMetrics(db.Model):
    # __bind_key__ = "metrics"
    __tablename__ = "weekly_metrics"

    # Shows the date for the previous week (as that's what the metrics cover.)
    previous_week = date.today() - timedelta(days=7)

    ID                                  =       db.Column(db.Integer, primary_key=True)
    WeekOf                              =       db.Column(db.DateTime, nullable=False, default=previous_week)
    ECCHostIncidents                    =       db.Column(db.Integer, nullable=False)
    Site24x7Incidents                   =       db.Column(db.Integer, nullable=False)
    NagiosIncidents                     =       db.Column(db.Integer, nullable=False)
    EDIIncidents                        =       db.Column(db.Integer, nullable=False)
    InfoSecIncidents                    =       db.Column(db.Integer, nullable=False)
    P1Incidents                         =       db.Column(db.Integer, nullable=False)
    StatusPageOutages                   =       db.Column(db.Integer, nullable=False)
    StatusPagePerformanceDegredations   =       db.Column(db.Integer, nullable=False)
    StatusPageMaintenances              =       db.Column(db.Integer, nullable=False)
    CodeChanges                         =       db.Column(db.Integer, nullable=False)
    TotalDailiesAlerts                  =       db.Column(db.Integer, nullable=False)
    DailiesAffectedServers              =       db.Column(db.Integer, nullable=False)
    DailiesRepeatedProblems             =       db.Column(db.Integer, nullable=False)
    SolarWindsIncidents                 =       db.Column(db.Integer, nullable=False)   


    def __init__(self, WeekOf, ECCHostIncidents, Site24x7Incidents, NagiosIncidents, EDIIncidents, 
        InfoSecIncidents, P1Incidents, StatusPageOutages, StatusPagePerformanceDegredations,
        StatusPageMaintenances, CodeChanges, TotalDailiesAlerts, DailiesAffectedServers,
        DailiesRepeatedProblems, SolarWindsIncidents):

        self.WeekOf = WeekOf
        self.ECCHostIncidents = ECCHostIncidents
        self.Site24x7Incidents = Site24x7Incidents
        self.NagiosIncidents = NagiosIncidents
        self.EDIIncidents = EDIIncidents
        self.InfoSecIncidents = InfoSecIncidents
        self.P1Incidents = P1Incidents
        self.StatusPageOutages = StatusPageOutages
        self.StatusPagePerformanceDegredations = StatusPagePerformanceDegredations
        self.StatusPageMaintenances = StatusPageMaintenances
        self.CodeChanges = CodeChanges
        self.TotalDailiesAlerts = TotalDailiesAlerts
        self.DailiesAffectedServers = DailiesAffectedServers
        self.DailiesRepeatedProblems = DailiesRepeatedProblems
        self.SolarWindsIncidents = SolarWindsIncidents

    def reset_table(self):
        db.session.execute("""TRUNCATE TABLE weekly_metrics RESTART IDENTITY;""")
        db.session.commit()

    def insert_data(self, WeekOf, ECCHostIncidents, Site24x7Incidents, NagiosIncidents, EDIIncidents, 
            InfoSecIncidents, P1Incidents, StatusPageOutages, StatusPagePerformanceDegredations,
            StatusPageMaintenances, CodeChanges, TotalDailiesAlerts, DailiesAffectedServers,
            DailiesRepeatedProblems, SolarWindsIncidents):
        try:
            post_data = {
                'WeekOf': WeekOf,
                'ECCHostIncidents': ECCHostIncidents,
                'Site24x7Incidents': Site24x7Incidents,
                'NagiosIncidents': NagiosIncidents,
                'EDIIncidents': EDIIncidents,
                'InfoSecIncidents': InfoSecIncidents,
                'P1Incidents': P1Incidents,
                'StatusPageOutages': StatusPageOutages,
                'StatusPagePerformanceDegredations': StatusPagePerformanceDegredations,
                'StatusPageMaintenances': StatusPageMaintenances,
                'CodeChanges': CodeChanges,
                'TotalDailiesAlerts': TotalDailiesAlerts,
                'DailiesAffectedServers': DailiesAffectedServers,
                'DailiesRepeatedProblems': DailiesRepeatedProblems,
                'SolarWindsIncidents': SolarWindsIncidents  
            }

            requests.post('http://localhost:5000/api/', json=post_data, verify=False)
            print("db insert success \n")
        except: 
            print("db insert error:", sys.exc_info()[0])
            raise

    def select_all():
        try:
            table_query = WeeklyMetrics.query.all()
            # for row in table_query:
            #     print({
            #     'WeekOf': row.WeekOf,
            #     'ECCHostIncidents': row.ECCHostIncidents,
            #     'Site24x7Incidents': row.Site24x7Incidents,
            #     'NagiosIncidents': row.NagiosIncidents,
            #     'EDIIncidents': row.EDIIncidents,
            #     'InfoSecIncidents': row.InfoSecIncidents,
            #     'P1Incidents': row.P1Incidents,
            #     'StatusPageOutages': row.StatusPageOutages,
            #     'StatusPagePerformanceDegredations': row.StatusPagePerformanceDegredations,
            #     'StatusPageMaintenances': row.StatusPageMaintenances,
            #     'CodeChanges': row.CodeChanges,
            #     'TotalDailiesAlerts': row.TotalDailiesAlerts,
            #     'DailiesAffectedServers': row.DailiesAffectedServers,
            #     'DailiesRepeatedProblems': row.DailiesRepeatedProblems,
            #     'SolarWindsIncidents': row.SolarWindsIncidents
            #     } , "\n")

            print("db select all success \n")
            return table_query
            
        except:
            print("db select all error:", sys.exc_info()[0])
            raise

    def select_filtered(self, **kwargs):
        try:
            # for testing
            if kwargs:
                print(kwargs)
            
            filter = WeeklyMetrics.query.filter_by(**kwargs)

            filter_all = filter.all()
            print(filter_all)

            filter_first_item = filter.first()
            print(filter_first_item)
            
            print("db select filtered success \n")
        except:
            print("db select filtered error:", sys.exc_info()[0])
            raise

    def delete_all(self):
        metrics_total = WeeklyMetrics.query.all()
        # num = each metric's ID in postgres (with their routes being: /api/1, /api/2, etc)
        for num in range(0, len(metrics_total)):
            try:
                requests.delete(f'http://localhost:5000/api/{num}')
            except:
                print(f"{num} is not available")

    def delete_item(self, **kwargs):
        try:
            if kwargs:
                table_query = WeeklyMetrics.query.filter_by(**kwargs).all()
                for row in table_query:
                    db.session.delete(row)
            else:
                table_query = WeeklyMetrics.query.all()
                print("What row(s) would you like to delete?  Try again.")

            db.session.commit()
            print("db delete success \n")
        except:
            print("db delete error:", sys.exc_info()[0])
            raise

    def print_all():
        try:
            table_query = WeeklyMetrics.query.all()
            for row in table_query:
                print({
                'WeekOf': row.WeekOf,
                'ECCHostIncidents': row.ECCHostIncidents,
                'Site24x7Incidents': row.Site24x7Incidents,
                'NagiosIncidents': row.NagiosIncidents,
                'EDIIncidents': row.EDIIncidents,
                'InfoSecIncidents': row.InfoSecIncidents,
                'P1Incidents': row.P1Incidents,
                'StatusPageOutages': row.StatusPageOutages,
                'StatusPagePerformanceDegredations': row.StatusPagePerformanceDegredations,
                'StatusPageMaintenances': row.StatusPageMaintenances,
                'CodeChanges': row.CodeChanges,
                'TotalDailiesAlerts': row.TotalDailiesAlerts,
                'DailiesAffectedServers': row.DailiesAffectedServers,
                'DailiesRepeatedProblems': row.DailiesRepeatedProblems,
                'SolarWindsIncidents': row.SolarWindsIncidents
                } , "\n")
                
            print("db print all success \n")
            
        except:
            print("db select all error:", sys.exc_info()[0])
            raise



## --------------------------------------------------------------------------------------------------------

class OpsgenieMetrics(db.Model):
    # __bind_key__ = "opsgenie"
    __tablename__ = "opsgenie_metrics"

    previous_week = date.today() - timedelta(days=7)

    ID                                  =       db.Column(db.Integer, primary_key=True)
    WeekOf                              =       db.Column(db.DateTime, nullable=False, default=previous_week)
    TotalCRCIncidentCount               =       db.Column(db.Integer, nullable=False)
    TotalCRCIncidentMTTA                =       db.Column(db.Time, nullable=False)
    TotalCRCIncidentMTTR                =       db.Column(db.Time, nullable=False)
    Nagios                              =       db.Column(db.Integer, nullable=False)
    Site24x7                            =       db.Column(db.Integer, nullable=False)
    Azure                               =       db.Column(db.Integer, nullable=False)
    DocStar                             =       db.Column(db.Integer, nullable=False)
    DocStarMTTA                         =       db.Column(db.Time, nullable=False)
    DocStarMTTR                         =       db.Column(db.Time, nullable=False)
    ECC                                 =       db.Column(db.Integer, nullable=False)
    ECCMTTA                             =       db.Column(db.Time, nullable=False)
    ECCMTTR                             =       db.Column(db.Time, nullable=False)
    EpicorGlobalERPSystems              =       db.Column(db.Integer, nullable=False)
    EpicorGlobalERPSystemsMTTA          =       db.Column(db.Time, nullable=False)
    EpicorGlobalERPSystemsMTTR          =       db.Column(db.Time, nullable=False)
    EpicorInfrastructure                =       db.Column(db.Integer, nullable=False)
    EpicorInfrastructureMTTA            =       db.Column(db.Time, nullable=False)
    EpicorInfrastructureMTTR            =       db.Column(db.Time, nullable=False)
    EpicorWebSitesAndFTP                =       db.Column(db.Integer, nullable=False)
    EpicorWebSitesAndFTPMTTA            =       db.Column(db.Time, nullable=False)
    EpicorWebSitesAndFTPMTTR            =       db.Column(db.Time, nullable=False)
    KineticEpicorERPCloud               =       db.Column(db.Integer, nullable=False)
    KineticEpicorERPCloudMTTA           =       db.Column(db.Time, nullable=False)
    KineticEpicorERPCloudMTTR           =       db.Column(db.Time, nullable=False)
    Prophet21Cloud                      =       db.Column(db.Integer, nullable=False)
    Prophet21CloudMTTA                  =       db.Column(db.Time, nullable=False)
    Prophet21CloudMTTR                  =       db.Column(db.Time, nullable=False)
    Quickship                           =       db.Column(db.Integer, nullable=False)
    QuickshipMTTA                       =       db.Column(db.Time, nullable=False)
    QuickshipMTTR                       =       db.Column(db.Time, nullable=False)
    EDISource                           =       db.Column(db.Integer, nullable=False)
    EDISourceMTTA                       =       db.Column(db.Time, nullable=False)
    EDISourceMTTR                       =       db.Column(db.Time, nullable=False)

    def __init__(self, TotalCRCIncidentCount, TotalCRCIncidentMTTA, TotalCRCIncidentMTTR,
        Nagios, Site24x7, Azure, DocStar, DocStarMTTA, DocStarMTTR, ECC, ECCMTTA, ECCMTTR,
        EpicorGlobalERPSystems, EpicorGlobalERPSystemsMTTA, EpicorGlobalERPSystemsMTTR,
        EpicorInfrastructure, EpicorInfrastructureMTTA, EpicorInfrastructureMTTR,
        EpicorWebSitesAndFTP, EpicorWebSitesAndFTPMTTA, EpicorWebSitesAndFTPMTTR,
        KineticEpicorERPCloud, KineticEpicorERPCloudMTTA, KineticEpicorERPCloudMTTR,
        Prophet21Cloud, Prophet21CloudMTTA, Prophet21CloudMTTR, Quickship, QuickshipMTTA, 
        QuickshipMTTR, EDISource, EDISourceMTTA, EDISourceMTTR):

        self.TotalCRCIncidentCount = TotalCRCIncidentCount
        self.TotalCRCIncidentMTTA = TotalCRCIncidentMTTA
        self.TotalCRCIncidentMTTR = TotalCRCIncidentMTTR
        self.Nagios = Nagios
        self.Site24x7 = Site24x7
        self.Azure = Azure
        self.DocStar = DocStar
        self.DocStarMTTA = DocStarMTTA
        self.DocStarMTTR = DocStarMTTR
        self.ECC = ECC
        self.ECCMTTA = ECCMTTA
        self.ECCMTTR = ECCMTTR
        self.EpicorGlobalERPSystems = EpicorGlobalERPSystems
        self.EpicorGlobalERPSystemsMTTA = EpicorGlobalERPSystemsMTTA
        self.EpicorGlobalERPSystemsMTTR = EpicorGlobalERPSystemsMTTR
        self.EpicorInfrastructure = EpicorInfrastructure
        self.EpicorInfrastructureMTTA = EpicorInfrastructureMTTA
        self.EpicorInfrastructureMTTR = EpicorInfrastructureMTTR
        self.EpicorWebSitesAndFTP = EpicorWebSitesAndFTP
        self.EpicorWebSitesAndFTPMTTA = EpicorWebSitesAndFTPMTTA
        self.EpicorWebSitesAndFTPMTTR = EpicorWebSitesAndFTPMTTR
        self.KineticEpicorERPCloud = KineticEpicorERPCloud
        self.KineticEpicorERPCloudMTTA = KineticEpicorERPCloudMTTA
        self.KineticEpicorERPCloudMTTR = KineticEpicorERPCloudMTTR
        self.Prophet21Cloud = Prophet21Cloud
        self.Prophet21CloudMTTA = Prophet21CloudMTTA
        self.Prophet21CloudMTTR = Prophet21CloudMTTR
        self.Quickship = Quickship
        self.QuickshipMTTA = QuickshipMTTA
        self.QuickshipMTTR = QuickshipMTTR
        self.EDISource = EDISource
        self.EDISourceMTTA = EDISourceMTTA
        self.EDISourceMTTR = EDISourceMTTR

    def reset_table(self):
        db.session.execute("""TRUNCATE TABLE weekly_metrics RESTART IDENTITY;""")
        db.session.commit()

    def insert_data(self, TotalCRCIncidentCount, TotalCRCIncidentMTTA, TotalCRCIncidentMTTR,
        Nagios, Site24x7, Azure, DocStar, DocStarMTTA, DocStarMTTR, ECC, ECCMTTA, ECCMTTR,
        EpicorGlobalERPSystems, EpicorGlobalERPSystemsMTTA, EpicorGlobalERPSystemsMTTR,
        EpicorInfrastructure, EpicorInfrastructureMTTA, EpicorInfrastructureMTTR,
        EpicorWebSitesAndFTP, EpicorWebSitesAndFTPMTTA, EpicorWebSitesAndFTPMTTR,
        KineticEpicorERPCloud, KineticEpicorERPCloudMTTA, KineticEpicorERPCloudMTTR,
        Prophet21Cloud, Prophet21CloudMTTA, Prophet21CloudMTTR, Quickship, QuickshipMTTA, 
        QuickshipMTTR, EDISource, EDISourceMTTA, EDISourceMTTR):
    
        try:
            post_data = {
                'TotalCRCIncidentCount': TotalCRCIncidentCount,
                'TotalCRCIncidentMTTA': TotalCRCIncidentMTTA,
                'TotalCRCIncidentMTTR': TotalCRCIncidentMTTR,
                'Nagios': Nagios,
                'Site24x7': Site24x7,
                'Azure': Azure,
                'DocStar': DocStar,
                'DocStarMTTA': DocStarMTTA,
                'DocStarMTTR': DocStarMTTR,
                'ECC': ECC,
                'ECCMTTA': ECCMTTA,
                'ECCMTTR': ECCMTTR,
                'EpicorGlobalERPSystems': EpicorGlobalERPSystems,
                'EpicorGlobalERPSystemsMTTA': EpicorGlobalERPSystemsMTTA,
                'EpicorGlobalERPSystemsMTTR': EpicorGlobalERPSystemsMTTR,
                'EpicorInfrastructure': EpicorInfrastructure,  
                'EpicorInfrastructureMTTA': EpicorInfrastructureMTTA,  
                'EpicorInfrastructureMTTR': EpicorInfrastructureMTTR,  
                'EpicorWebSitesAndFTP': EpicorWebSitesAndFTP,  
                'EpicorWebSitesAndFTPMTTA': EpicorWebSitesAndFTPMTTA,  
                'EpicorWebSitesAndFTPMTTR': EpicorWebSitesAndFTPMTTR,  
                'KineticEpicorERPCloud': KineticEpicorERPCloud,  
                'KineticEpicorERPCloudMTTA': KineticEpicorERPCloudMTTA,  
                'KineticEpicorERPCloudMTTR': KineticEpicorERPCloudMTTR,  
                'Prophet21Cloud': Prophet21Cloud,  
                'Prophet21CloudMTTA': Prophet21CloudMTTA,  
                'Prophet21CloudMTTR': Prophet21CloudMTTR,  
                'Quickship': Quickship,  
                'QuickshipMTTA': QuickshipMTTA,  
                'QuickshipMTTR': QuickshipMTTR,  
                'EDISource': EDISource,  
                'EDISourceMTTA': EDISourceMTTA,  
                'EDISourceMTTR': EDISourceMTTR
            }

            requests.post('http://localhost:5000/api/', json=post_data, verify=False)
            print("db insert success \n")
        except: 
            print("db insert error:", sys.exc_info()[0])
            raise


    def select_all(self):
        try:
            table_query = OpsgenieMetrics.query.all()
            for row in table_query:
                print({
                'TotalCRCIncidentCount': row.TotalCRCIncidentCount,
                'TotalCRCIncidentMTTA': row.TotalCRCIncidentMTTA,
                'TotalCRCIncidentMTTR': row.TotalCRCIncidentMTTR,
                'Nagios': row.Nagios,
                'Site24x7': row.Site24x7,
                'Azure': row.Azure,
                'DocStar': row.DocStar,
                'DocStarMTTA': row.DocStarMTTA,
                'DocStarMTTR': row.DocStarMTTR,
                'ECC': row.ECC,
                'ECCMTTA': row.ECCMTTA,
                'ECCMTTR': row.ECCMTTR,
                'EpicorGlobalERPSystems': row.EpicorGlobalERPSystems,
                'EpicorGlobalERPSystemsMTTA': row.EpicorGlobalERPSystemsMTTA,
                'EpicorGlobalERPSystemsMTTR': row.EpicorGlobalERPSystemsMTTR,
                'EpicorInfrastructure': row.EpicorInfrastructure,  
                'EpicorInfrastructureMTTA': row.EpicorInfrastructureMTTA,  
                'EpicorInfrastructureMTTR': row.EpicorInfrastructureMTTR,  
                'EpicorWebSitesAndFTP': row.EpicorWebSitesAndFTP,  
                'EpicorWebSitesAndFTPMTTA': row.EpicorWebSitesAndFTPMTTA,  
                'EpicorWebSitesAndFTPMTTR': row.EpicorWebSitesAndFTPMTTR,  
                'KineticEpicorERPCloud': row.KineticEpicorERPCloud,  
                'KineticEpicorERPCloudMTTA': row.KineticEpicorERPCloudMTTA,  
                'KineticEpicorERPCloudMTTR': row.KineticEpicorERPCloudMTTR,  
                'Prophet21Cloud': row.Prophet21Cloud,  
                'Prophet21CloudMTTA': row.Prophet21CloudMTTA,  
                'Prophet21CloudMTTR': row.Prophet21CloudMTTR,  
                'Quickship': row.Quickship,  
                'QuickshipMTTA': row.QuickshipMTTA,  
                'QuickshipMTTR': row.QuickshipMTTR,  
                'EDISource': row.EDISource,  
                'EDISourceMTTA': row.EDISourceMTTA,  
                'EDISourceMTTR': row.EDISourceMTTR
                } , "\n")
            print("db select all success \n")
            return table_query

        except:
            print("db select all error:", sys.exc_info()[0])
            raise
        

    def select_filtered(self, **kwargs):
        try:
            # for testing
            if kwargs:
                print(kwargs)
            
            filter = OpsgenieMetrics.query.filter_by(**kwargs)

            filter_all = filter.all()
            print(filter_all)

            filter_first_item = filter.first()
            print(filter_first_item)
            
            print("db select filtered success \n")
        except:
            print("db select filtered error:", sys.exc_info()[0])
            raise

    def delete_all(self):
        metrics_total = OpsgenieMetrics.query.all()
        # num = each metric's ID in postgres (with their routes being: /api/1, /api/2, etc)
        for num in range(0, len(metrics_total)):
            try:
                requests.delete(f'http://localhost:5000/api/{num}')
            except:
                print(f"{num} is not available")

    def delete_item(self, **kwargs):
        try:
            if kwargs:
                table_query = OpsgenieMetrics.query.filter_by(**kwargs).all()
                for row in table_query:
                    db.session.delete(row)
            else:
                table_query = OpsgenieMetrics.query.all()
                print("What row(s) would you like to delete?  Try again.")

            db.session.commit()
            print("db delete success \n")
        except:
            print("db delete error:", sys.exc_info()[0])
            raise

