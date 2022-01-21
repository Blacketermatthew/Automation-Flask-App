from io import BytesIO
import xlsxwriter
import requests
import json
import csv
import os
import urllib3
from getpass import getuser
from datetime import date
from time import sleep
# this is for environmental variables to store API keys
from dotenv import load_dotenv
# This will suppress the certificate warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# --------------- VARIABLES -------------------------------------------

# Traditional variables from .env
load_dotenv()  # loads the .env file
NONPCI_KEY = os.getenv('NON_PCI_KEY')
PCI_KEY = os.getenv('PCI_KEY')
IRV_KEY = os.getenv('IRV_KEY')
UK_KEY = os.getenv('UK_KEY')
EMS_KEY = os.getenv('EMS_KEY')
SYD_KEY = os.getenv('SYD_KEY')

# Variables that will be found inside the Heroku app
# NONPCI_KEY = os.environ.get("NON_PCI_KEY")
# PCI_KEY = os.environ.get("PCI_KEY")
# IRV_KEY = os.environ.get("IRV_KEY")
# UK_KEY = os.environ.get("UK_KEY")
# EMS_KEY = os.environ.get("EMS_KEY")
# SYD_KEY = os.environ.get("SYD_KEY")

##########################################################################################
# VARIABLES REDACTED
# nonpci_url
# pci_url
# irv_url
# uk_url
# ems_url
# syd_url
#########################################################################################

boards = {nonpci_url: "NonPCI", pci_url: "PCI", irv_url: "Irvine",
          uk_url: "UK", ems_url: "EMS", syd_url: "Sydney"}
# Gets the values from the boards dict to name the excel sheets
boardnames = [name for url, name in boards.items()]
# This loop goes through each Nagios board, grabs each hostname and its IP address, then puts them into a single list.
# From there, it creates a spreadsheet and pastes the list into the cells, then places the .csv's on your desktop.


def grabber():

    list_of_board_dicts = []

    for k, v in boards.items():

        # submits a GET request for the specified board in boards
        # verify=False is to ignore cert issues
        r_host = requests.get(k, verify=False, timeout=5)
        sleep(2)

        r_host_json = r_host.json()  # Converts it to json
        # r_host_pretty = json.dumps(r_host_json, indent=2)   # Mainly for looking at the entire code in a viewer-friendly fashion

        # This grabs the host names and IP Addresses on a specific board and adds them to the empty dictionary
        board_dict = {}
        for x in reversed(range(int(r_host_json['recordcount']))):
            board_dict[r_host_json['host'][x]['host_name']
                       ] = r_host_json['host'][x]['address']

        list_of_board_dicts.append(board_dict)
        r_host.close()

    return list_of_board_dicts


# Creates a variable for the list of dicts of each board's hostname and IP
board_dicts_list = grabber()


# -----------------------------------

def workbook_creator():

    # Creates an excel workbook
    file = BytesIO()
    workbook = xlsxwriter.Workbook(file)

    # Creates a list of worksheets named after each Nagios board
    worksheets = []
    for i in range(len(board_dicts_list)):
        worksheets.append(workbook.add_worksheet('{}'.format(boardnames[i])))

    # Populates each spreadsheet with its respective Nagios board's hostnames
    for n in range(len(board_dicts_list)):
        row = 0
        col = 0
        for key, value in board_dicts_list[n].items():
            worksheets[n].write(row, col, key)
            row += 1

    # Populates each spreadsheet with its respective Nagios board's IP (next to its hostname)
    for r in range(len(board_dicts_list)):
        row = 0
        col = 1
        for key, value in board_dicts_list[r].items():
            worksheets[r].write(row, col, value)
            row += 1

    workbook.close()
    file.seek(0)

    return file
