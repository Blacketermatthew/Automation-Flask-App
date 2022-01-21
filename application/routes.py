#from application.scripts.nagios_inv_grab import grabber, workbook_creator
from werkzeug.security import generate_password_hash, check_password_hash
from . import app, api
from flask import url_for, render_template, flash, redirect, send_file, Response, request, session, jsonify, make_response
from .scripts.snow_phish_checkandclose import ticket_list_creator, team_list_grabber, phish_closer, closeable_ticket_grabber
from .scripts.site24x7_ticket_closer import site24x7_closer
from .scripts.agios_ticket_closer import agios_closer
from .scripts.site24x7_custom_note_closer import site24x7_custom_closer
from .scripts.agios_custom_note_closer import agios_custom_closer
from .models import User, db, WeeklyMetrics, OpsgenieMetrics
from .forms import LoginForm
from metric_data import post_all
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Resource  # class that handles API requests
import requests
# this is for environmental variables to store API keys
from dotenv import load_dotenv
import os
import sys
from io import StringIO
import csv

######                              ######################################################################################
###### Variable/Environment Setup   ######################################################################################
######                              ######################################################################################

# Traditional variables from .env
load_dotenv()  # loads the .env file

# Used to configure the app when it's deployed to Heroku
if os.environ.get("IS_HEROKU"):
    is_heroku = True
    heroku_user = os.environ.get("HEROKU_USERNAME")
    heroku_pass = generate_password_hash(os.environ.get("HEROKU_PASSWORD"))

# Configures the app when it's ran locally and variables are pulled from .env
elif os.getenv("IS_DEV"):
    is_dev = True
    heroku_user = os.getenv("HEROKU_USERNAME")
    heroku_pass = generate_password_hash(os.getenv("HEROKU_PASSWORD"))

else:
    print("NEITHER HEROKU NOR DEV")


######   API    #############################################################################################################
######  Routes  #############################################################################################################
######          #############################################################################################################

@api.route("/api", methods=['GET', 'POST', 'PUT', 'DELETE'])
@api.route("/api/", methods=['GET', 'POST', 'PUT', 'DELETE'])
class GetAndPost(Resource):

    def post(self):

        if request.method == "POST":
            # returns the incoming json data given during a post request
            data = request.json

            # creates a new WeeklyMetrics entry with the data submitted in the post request
            post_data = WeeklyMetrics(
                WeekOf=data['WeekOf'],
                ECCHostIncidents=data['ECCHostIncidents'],
                Site24x7Incidents=data['Site24x7Incidents'],
                NagiosIncidents=data['NagiosIncidents'],
                EDIIncidents=data['EDIIncidents'],
                InfoSecIncidents=data['InfoSecIncidents'],
                P1Incidents=data['P1Incidents'],
                StatusPageOutages=data['StatusPageOutages'],
                StatusPagePerformanceDegredations=data['StatusPagePerformanceDegredations'],
                StatusPageMaintenances=data['StatusPageMaintenances'],
                CodeChanges=data['CodeChanges'],
                TotalDailiesAlerts=data['TotalDailiesAlerts'],
                DailiesAffectedServers=data['DailiesAffectedServers'],
                DailiesRepeatedProblems=data['DailiesRepeatedProblems'],
                SolarWindsIncidents=data['SolarWindsIncidents'])

            # adds it to the database and saves it
            db.session.add(post_data)
            db.session.commit()

            print("postsuccess")
            return {"message": f"The metrics have been successfully added."}

        else:
            print("posterror", sys.exc_info()[0])
            return {"error": "The request payload is not in JSON format"}

    def get(self):

        # retrieves all the database entries
        total_weekly_metrics = WeeklyMetrics.query.all()
        get_data = [
            {
                "WeekOf": metric.WeekOf.strftime('%m-%d-%Y'),
                "ECCHostIncidents": metric.ECCHostIncidents,
                "Site24x7Incidents": metric.Site24x7Incidents,
                "NagiosIncidents": metric.NagiosIncidents,
                "EDIIncidents": metric.EDIIncidents,
                "InfoSecIncidents": metric.InfoSecIncidents,
                "P1Incidents": metric.P1Incidents,
                "StatusPageOutages": metric.StatusPageOutages,
                "StatusPagePerformanceDegredations": metric.StatusPagePerformanceDegredations,
                "StatusPageMaintenances": metric.StatusPageMaintenances,
                "CodeChanges": metric.CodeChanges,
                "TotalDailiesAlerts": metric.TotalDailiesAlerts,
                "DailiesAffectedServers": metric.DailiesAffectedServers,
                "DailiesRepeatedProblems": metric.DailiesRepeatedProblems,
                "SolarWindsIncidents": metric.SolarWindsIncidents,
            } for metric in total_weekly_metrics]

        return {"count": len(get_data), "total_weekly_metrics": get_data}


api.add_resource(GetAndPost, '/api')

# Same as the above route, but lets you specify the metric


# Takes an index parameter to find a specific object
@api.route('/api/<metric_id>', methods=['GET', 'PUT', 'DELETE'])
class WeeklyMetricsClass(Resource):

    def get(self, metric_id):
        metric = WeeklyMetrics.query.get_or_404(metric_id)
        get_data = {
            "WeekOf": metric.WeekOf.strftime('%m-%d-%Y'),
            "ECCHostIncidents": metric.ECCHostIncidents,
            "Site24x7Incidents": metric.Site24x7Incidents,
            "NagiosIncidents": metric.NagiosIncidents,
            "EDIIncidents": metric.EDIIncidents,
            "InfoSecIncidents": metric.InfoSecIncidents,
            "P1Incidents": metric.P1Incidents,
            "StatusPageOutages": metric.StatusPageOutages,
            "StatusPagePerformanceDegredations": metric.StatusPagePerformanceDegredations,
            "StatusPageMaintenances": metric.StatusPageMaintenances,
            "CodeChanges": metric.CodeChanges,
            "TotalDailiesAlerts": metric.TotalDailiesAlerts,
            "DailiesAffectedServers": metric.DailiesAffectedServers,
            "DailiesRepeatedProblems": metric.DailiesRepeatedProblems,
            "SolarWindsIncidents": metric.SolarWindsIncidents,
        }

        return {"message": "success", "metric": get_data}

    def put(self, metric_id):
        metric = WeeklyMetrics.query.get_or_404(metric_id)
        data = request.json

        metric.ID = data['ID']
        metric.ECCHostIncidents = data['ECCHostIncidents'],
        metric.Site24x7Incidents = data['Site24x7Incidents'],
        metric.NagiosIncidents = data['NagiosIncidents'],
        metric.EDIIncidents = data['EDIIncidents'],
        metric.InfoSecIncidents = data['InfoSecIncidents'],
        metric.P1Incidents = data['P1Incidents'],
        metric.StatusPageOutages = data['StatusPageOutages'],
        metric.StatusPagePerformanceDegredations = data['StatusPagePerformanceDegredations'],
        metric.StatusPageMaintenances = data['StatusPageMaintenances'],
        metric.CodeChanges = data['CodeChanges'],
        metric.TotalDailiesAlerts = data['TotalDailiesAlerts'],
        metric.DailiesAffectedServers = data['DailiesAffectedServers'],
        metric.DailiesRepeatedProblems = data['DailiesRepeatedProblems'],
        metric.SolarWindsIncidents = data['SolarWindsIncidents']
        db.session.add(metric)
        db.session.commit()

        return {"message": f"The metrics have been successfully updated!"}

    def delete(self, metric_id):
        metric = WeeklyMetrics.query.get_or_404(metric_id)

        db.session.delete(metric)
        db.session.commit()

        return {"message": f"The metrics have been successfully deleted!"}


api.add_resource(WeeklyMetricsClass, '/api')


######   app    #############################################################################################################
######  Routes  #############################################################################################################
######          #############################################################################################################


######## Test routes ####################################
###############################

# Created a button to run scripts and run tests in the background while app is running
@app.route('/testing', methods=['GET', 'POST', 'DELETE'])
def test_func():
    return redirect(url_for('index'))

# Recreates tables from models.py


@app.route('/testing/createall', methods=['GET', 'POST', 'DELETE'])
def test_create_all():
    db.create_all()
    return redirect(url_for('index'))

# Deletes all tables from database


@app.route('/testing/dropmetrics', methods=['GET', 'POST', 'DELETE'])
def test_drop_metrics():
    db.drop_all(bind='metrics')
    return redirect(url_for('index'))


@app.route('/testing/postmetrics', methods=['GET', 'POST', 'DELETE'])
def test_post_metrics():
    post_all()
    return redirect(url_for('index'))


######## App routes #########################################################
###############################

@app.route("/error")
def not_found():
    return jsonify(message='That resource was not found.'), 404


@app.route("/login", methods=['GET', 'POST'])
def login():
    if session.get('username'):
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User(username=username, password=password)

        # If the username is correct and the password given matches the hashed password from Heroku
        if user.username == heroku_user and check_password_hash(heroku_pass, user.password):
            session['username'] = user.username
            return redirect("/index")
        else:
            flash("Sorry, something went wrong.", category="error")

    return render_template("login.html", form=form, login=True)


# Logs you out then redirects you to the index (which redirects you to /login if you aren't logged in.  Should I cut the middle man out?)
@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


# For the main page.  Displays index.html
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def index():
    if not session.get('username'):
        return redirect(url_for('login'))

    # Runs a function to return a dictionary with the CRC team and their SNOW sys_id's
    crc_team_dict = team_list_grabber()
    return render_template('index.html', crc_team_dict=crc_team_dict, index=True)


@app.route('/results', methods=['GET', 'POST'])
def button_results():

    try:
        crc_team_dict = team_list_grabber()
        crc_member = request.form.get('chosen_member')
    except:
        flash("Error: No CRC member was selected.", category="error")

    try:
        if request.form['action']:
            if request.form['action'] == 'KnowBe4 Phishing':
                ticket_list_return = ticket_list_creator(sys_id=crc_member)
                closeable_incs = closeable_ticket_grabber(
                    ticket_list=ticket_list_return['inc_sys_id_list'])
                response = phish_closer(request_status_code=ticket_list_return['inc_response'].status_code,
                                        ticket_list=ticket_list_return['inc_sys_id_list'], closeable_inc_list=closeable_incs, sys_id=crc_member)
            elif request.form['action'] == 'Site24x7':
                response = site24x7_closer(sys_id=crc_member)
            elif request.form['action'] == 'Agios':
                response = agios_closer(sys_id=crc_member)
            elif request.form['action'] == "Site24x7 Custom":
                textbox_close_notes = request.form.get('custom_text_input')
                response = site24x7_custom_closer(
                    sys_id=crc_member, customized_close_notes=textbox_close_notes)
            elif request.form['action'] == "Agios Custom":
                textbox_close_notes = request.form.get('custom_text_input')
                response = agios_custom_closer(
                    sys_id=crc_member, customized_close_notes=textbox_close_notes)
            else:
                flash("ALERT ALERT", "danger")

            flash(response['message'], category=response['flash_category'])

        else:
            print("Request form action: N/A")

    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise

    return render_template('results.html')


@app.route('/custom_notes', methods=['GET', 'POST'])
def custom_notes():
    crc_team_dict = team_list_grabber()
    flash("What would you like the close note to say?", "info")
    return render_template('custom_notes.html', crc_team_dict=crc_team_dict)


@app.route('/weekly_metrics', methods=['GET', 'POST'])
def get_weekly_metrics():
    weekly_db = WeeklyMetrics.select_all()
    return render_template('weekly_metrics.html', weekly_db=weekly_db)


@app.route('/export_data', methods=['GET', 'POST'])
def export_data():
    metric_headings = ['WeekOf', 'ECCHostIncidents', 'Site24x7Incidents', 'NagiosIncidents', 'EDIIncidents', 'InfoSecIncidents',
                       'P1Incidents', 'StatusPageOutages', 'StatusPagePerformanceDegredations', 'StatusPageMaintenances', 'CodeChanges',
                       'TotalDailiesAlerts', 'DailiesAffectedServers', 'DailiesRepeatedProblems', 'SolarWindsIncidents']
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(metric_headings)
    for metric in WeeklyMetrics.query.all():
        cw.writerow([str(getattr(metric, col)) for col in metric_headings])
        # print([str(getattr(metric, col)) for col in headings])

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=Total Weekly Metrics.csv"
    output.headers["Content-type"] = "text/csv"

    return output
