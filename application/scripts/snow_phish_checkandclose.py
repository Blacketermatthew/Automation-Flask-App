import requests
import urllib3
import json
import os
from os import environ, getenv
import sys
# this is for environmental variables to store API keys
from dotenv import load_dotenv
# This will suppress any certificate warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

####################################################################################################################################################
# Main purpose of script: To close any open KnowBe4 tickets assigned to you that have both of their child tasks completed by Tier-2/Tier-3/InfoSec #
# Notes:                                                                                                                                           #
#       Incident API states: 1. New | 2. In Progress | 3. On Hold | 6. Resolved | 7. Closed | 8. Canceled                                              #
#       Task API states: -1. Open | 0. Review | 2. Pending | 3. Closed Complete                                                                        #                                                                                                                                                 #
####################################################################################################################################################


# --- Variables ---------------------------------------------

# Traditional variables from .env
load_dotenv()  # loads the .env file

# Used to configure the app when it's deployed to Heroku
if os.environ.get("IS_HEROKU"):
    user = os.environ.get("NAGIOS_INTEGRATION_SNOW_USERNAME")
    passwd = os.environ.get("NAGIOS_INTEGRATION_SNOW_PASSWORD")

# Configures the app when it's ran locally and variables are pulled from .env
elif os.getenv("IS_DEV"):
    user = os.getenv("NAGIOS_ENV_USER")
    passwd = os.getenv("NAGIOS_ENV_PASSWD")

else:
    print("FALSE")

##########################################################################################
# VARIABLES REDACTED
# task_api_url
# inc_api_url
# sys_user_api_url
# knowbe4_id
# crc_dept
#########################################################################################


# This is the required information that will be added to the tickets upon their closure.
data = {'business_service': 'InfoSec',
        'close_code': 'Solved Remotely (Work Around)',
        'close_notes': 'The child tasks for this ticket have been completed.  This ticket was closed using via API.  Please reach out to the CRC if you have any questions or concerns.',
        'incident_state': '6'
        }


# ---- Functions ----------------------

# This grabs all phishing tickets assigned to you that are placed On Hold.
def ticket_list_creator(sys_id=""):

    # NOTE: The 'assigned_to' parameter must be changed to your own id. (verify=False ignores a cert error)
    inc_response = requests.get(inc_api_url,
                                auth=(user, passwd),
                                verify=False,
                                params={"sys_created_by": knowbe4_id,
                                        "assigned_to": sys_id,
                                        "active": "true",
                                        "incident_state": "3"
                                        })

    inc_json = inc_response.json()
    try:
        inc_sys_id_list = [inc_json['result'][x]['sys_id'] for x in range(len(
            inc_json['result']))]  # Creates a list of the sys_ids of all your open incidents
    except KeyError:
        inc_sys_id_list = []

    ticket_list_creator_dict = {'inc_response': inc_response,
                                'inc_json': inc_json, 'inc_sys_id_list': inc_sys_id_list, 'sys_id': sys_id}
    return ticket_list_creator_dict


# This function uses the list of open incidents and loops through them, grabbing their child incident task's states in the process.
# If both tasks have been finished by Tier-2 and InfoSec (and the tasks are closed complete), they'll be placed in a list for later use.
def closeable_ticket_grabber(ticket_list=[]):

    # An empty list that gets filled whenever there are incident tickets able to be closed.
    closeable_incs = []

    if ticket_list != []:
        print("")  # print(ticket_list)

    for num in range(len(ticket_list)):
        try:
            # This grabs all the tasks on each ticket
            task_response = requests.get(task_api_url,
                                         auth=(user, passwd),
                                         verify=False,
                                         params={'incident': ticket_list[num]})

            task_json = task_response.json()  # Converts it to json
            # Made because this part gets typed OFTEN
            t_result = task_response.json()['result']

            # If both tasks are Closed Complete (state = 3) and/or Closed Incomplete (state = 4),
            #  their parent incident's sys_id is put into a list for later.
            if ((t_result[0]['state'] == "3" and t_result[1]['state'] == "3")
                or (t_result[0]['state'] == "3" and t_result[1]['state'] == "4")
                or (t_result[0]['state'] == "4" and t_result[1]['state'] == "3")
                    or (t_result[0]['state'] == "4" and t_result[1]['state'] == "4")):

                # This grabs the sys_id of the task's parent incident
                closeable_incs.append(t_result[0]['incident']['value'])

            else:
                continue

        except:
            continue

    return closeable_incs


# This function checks to see if there are phishing tickets in your queue.  Then it checks the list from closeable_ticket_grabber() to see if any can be resolved.
def phish_closer(request_status_code=0, ticket_list=[], closeable_inc_list=[], sys_id=""):

    closed_ticket_count = 0

    if request_status_code == 200:  # If tickets are present, status_code == 200
        try:
            # Loops based on how many open tickets there are
            for inc in range(len(closeable_inc_list)):
                # Resolves the ticket if both incident tasks are Closed Complete.
                requests.put(inc_api_url + '/' + closeable_inc_list[inc], auth=(
                    user, passwd), verify=False, data=str(data))
                closed_ticket_count += 1

            phish_closer_dict = {
                'flash_category': 'success',
                'message': f"{len(ticket_list)} open tickets checked.  {closed_ticket_count} phishing ticket(s) assigned to you have been closed."}

        except KeyError:
            # return "KeyError: Some tickets may not have been closed.  Please review."
            print("Unexpected error:", sys.exc_info()[0])
            raise

    elif request_status_code == 404:
        phish_closer_dict = {
            'flash_category': 'danger',
            'message': f"Error code: {str(request_status_code)} - Either all of your tickets are still being worked on or you don't have any tickets assigned to you."}

    else:
        phish_closer_dict = {
            'flash_category': 'info',
            'message': f"Error code: {str(request_status_code)} - Unknown issue.  Please try again or investigate the issue."}

    return phish_closer_dict


####
# This function is used in routes.py to retrieve every CRC member then place their name and sys_id (used in many
#       ticket closing scripts).  The dictionary is used for member select dropdown menus
def team_list_grabber():
    try:
        team_list_response = requests.get(sys_user_api_url, auth=(user, passwd), verify=False,
                                          params={"department": crc_dept,
                                                  "title": "Cloud R Specialist"},
                                          timeout=5)
        team_json = team_list_response.json()  # Converts it to json
        team_dict = {}

        # This just organizes the names in the list alphabetically.
        team_dict = dict(sorted(team_dict.items()))

    except KeyError as e:
        print(team_list_response)
        print("Error:", e)

    return team_dict
