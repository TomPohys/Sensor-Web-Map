#!/home/tom/Documents/Project/Flask/map_portal/new_env app.py
# -*- coding: utf-8 -*-

# for folium 0.2
# Autor: Tomas Pohanka
# Department of Geoinformatics
# University of Palacky in Olomouc, Czech Republic
#==============================================================

CATEGORIES = {
    'CA': 'temperature',
    'CB': 'humidity',
    'ST': 'temperature',
    'SH': 'humidity',
    'CC': 'CO2',
    'CD': 'NO2',
    'CE': 'VOC',
    'CF': 'AP',
    'WA': 'wind speed',
    'WV': 'wind direction',
    'WP': 'rainfall',
    'BAT': 'battery'
}

ICON_URL = 'static/orez.png'
MAP_CENTER = [49.575676, 17.2840108]
PICTURE_COORS = [49.57645, 17.28229], [49.5728, 17.28735]

import flask
import folium
# because 'plugins' is folder
from folium import plugins
import vincent
#import random
import psycopg2
import json
#import pandas as pd
import datetime
import time
#import numpy as np

app = flask.Flask(__name__)

# TODO:
# Sensors in database, with timestamp of beginning of measurement
# and timestamp of end of measurement on the coords.

# day, month, year - not read from database, create variables
# for every month, create number of days - dictionary

SENSOR = [
    [382549735, (49.5746283, 17.2853339), '2015-04-20', '2015-09-23 23:59:59'],
    [382552362, (49.5755553, 17.2834242), '2015-04-20', '2015-05-20 23:59:59'],
    [382542829, (49.5752631, 17.2850897), '2015-04-24', '2015-08-18 23:59:59'],
    [382552190, (49.5750858, 17.2861411), '2015-04-27', '2015-05-06 23:59:59'],
    [382552190, (49.5755553, 17.2834242), '2015-06-04', '2015-07-09 23:59:59'],
    [382554362, (49.5755553, 17.2834242), '2015-07-23', '2015-09-03 23:59:59'],
    [382543190, (49.5737386, 17.2834661), '2015-07-23', '2015-07-23 23:59:59'],
    [382554362, (49.5734422, 17.2847517), '2015-09-03', '2015-09-08 23:59:59'],
    [382542829, (49.5738283, 17.2847464), '2015-09-03', '2015-09-23 23:59:59'],
    [382553190, (49.5734422, 17.2847517), '2015-09-08', '2016-09-10 23:59:59'],
    [382553190, (49.5737386, 17.2834661), '2016-10-01', '2016-10-01 23:59:59'],
    [382549735, (49.5746283, 17.2853339), '2015-10-01', '2015-11-25 23:59:59'],
    [382542829, (49.5738283, 17.2847464), '2015-10-01', '2015-11-02 23:59:59'],
    [382553931, (49.5737386, 17.2834661), '2015-11-10', '2015-11-10 23:59:59'],
    [382553748, (49.5734422, 17.2847517), '2015-11-23', '2016-11-30 23:59:59'],
    [382542735, (49.5737386, 17.2834661), '2015-12-17', '2015-12-17 23:59:59'],
    [382553362, (49.5734422, 17.2847517), '2015-12-15', '2015-12-24 23:59:59'],
    [382537776, (49.5746283, 17.2853339), '2015-12-17', '2015-12-22 23:59:59'],
    [382542735, (49.5738283, 17.2847464), '2016-01-04', '2016-02-13 23:59:59'],
    [382537776, (49.5746283, 17.2853339), '2016-01-13', '2016-02-29 23:59:59'],
    [382553159, (49.5734422, 17.2847517), '2016-01-04', '2016-01-18 23:59:59'],
    [382542829, (49.5738283, 17.2847464), '2016-02-16', '2016-02-29 23:59:59'],
    [382537362, (49.5734422, 17.2847517), '2016-02-16', '2016-02-29 23:59:59'],
    [382537437, (49.5737367, 17.2834439), '2016-02-16', '2016-02-29 23:59:59'],
    [38255931, (49.5737386, 17.2834661), '2016-02-16', '2016-02-29 23:59:59']
]

start_ask = time.time()
conn = psycopg2.connect(
    "dbname='db' user='postgres' host='localhost' password='postgres'")
cur = conn.cursor()

#print time.time() - start_ask
dates = []
month = []
m_type = []
error = ''
start_cats = time.time()
dates = range(1,32,1)
month = ['4/2015', '5/2015', '6/2015', '7/2015', '8/2015', '9/2015', '10/2015', '11/2015', '12/2015','1/2016', '2/2016']
for cat in CATEGORIES.values():
    m_type.append(cat)

#print time.time() - start_cats

@app.route('/', methods=['GET'])
def index():
    if flask.request.args.get('date') == None:

        return flask.render_template('index.html', dates=dates, phenom=m_type, months=month)

    date = int(flask.request.args.get('date'))
    month_selected = flask.request.args.get('months')
    phenom_long = flask.request.args.get('phenom')
    duration = int(flask.request.args.get('duration'))
    for key, name in CATEGORIES.iteritems():
        if name == phenom_long:
            phenom = key
    
    
    choosed_month, year = month_selected.split('/')
    try:
        start_date = datetime.datetime(int(year), int(choosed_month), date, 00, 00, 00)
        end_date = datetime.datetime(int(year), int(choosed_month), date, 23, 59, 59) + \
        datetime.timedelta(days=duration)
    except:
        return flask.render_template('error.html', dates=dates, phenom=m_type, months=month, error = 'date')

        

    # http://stackoverflow.com/questions/12438990/select-records-from-postgres-where-timestamp-is-in-certain-rangsoure
    if phenom_long == 'temperature':
        sql_sensor = "SELECT DISTINCT idsensor FROM data where (timestamp > '%s' and timestamp < '%s') and (measuretype = 'CA' or measuretype = 'ST');" % (
            start_date, end_date)

    elif phenom_long == 'humidity':
        sql_sensor = "SELECT DISTINCT idsensor FROM data where (timestamp > '%s' and timestamp < '%s') and (measuretype = 'CB' or measuretype = 'SH');" % (
            start_date, end_date)
    else:
        sql_sensor = "SELECT DISTINCT idsensor FROM data where (timestamp > '%s' and timestamp < '%s') and measuretype = '%s';" % (
            start_date, end_date, str(phenom))

    holice_map = folium.Map(MAP_CENTER, zoom_start=18, tiles=None)
    folium.TileLayer('OpenStreetMap').add_to(holice_map)
    folium.TileLayer('MapQuestOpen').add_to(holice_map)
    # Map.add_children(folium.plugins.ImageOverlay(...))
    # ICON_URL = 'static/python.jpg'
    holice_map.add_children(plugins.ImageOverlay(ICON_URL, [PICTURE_COORS], opacity=0.5,))
    # folium.LayerControl().add_to(holice_map)
    holice_map.add_children(folium.LayerControl())
    
    cur.execute(sql_sensor)
    # list of sensors [int,int,int], instead of [(int,), (int,), (int,)]
    sensors = [i[0] for i in cur.fetchall()]

    multi_iter1 = {}
    locations, popups = [], []
    for sensor_sql in sensors:
        # print sensor_sql
        
        for sensor in SENSOR:
            # print sensor
            if sensor[0] == sensor_sql:
                sensor_start_date = datetime.datetime.strptime(sensor[2], "%Y-%m-%d")
                sensor_end_date = datetime.datetime.strptime(sensor[3], "%Y-%m-%d %H:%M:%S")
                start_date_new = start_date
                end_date_new = end_date
                # print str(end_date) + ' > ' + str(sensor_start_date)
                # sensor have to not end measurement before start date and not start measurement after the end of end day
                if end_date >= sensor_start_date and start_date <= sensor_end_date:
                    # if sensor start measurement after start day, the start day will be replaced by sensor start day
                    # if value of start_date and end_date will be replaced, end of sensor measurement after end_date will not be replaced
                    if sensor_start_date > start_date:
                        #print start_date, sensor_start_date
                        start_date_new = sensor_start_date
                    if sensor_end_date < end_date:
                        #print end_date, sensor_end_date
                        end_date_new = sensor_end_date # + datetime.timedelta(days=duration)
                        
                    sensor_data = {}
                    if phenom_long == 'temperature':
                        sql_data_sensor = "SELECT measurevalue, timestamp FROM data WHERE (timestamp > '%s' and timestamp < '%s') and (measuretype = 'CA' or measuretype = 'ST') and idsensor = %d;" % (
                            start_date_new, end_date_new, int(sensor[0]))
                    elif phenom_long == 'humidity':
                        sql_data_sensor = "SELECT measurevalue, timestamp FROM data WHERE (timestamp > '%s' and timestamp < '%s') and (measuretype = 'CB' or measuretype = 'SH') and idsensor = %d;" % (
                            start_date_new, end_date_new, int(sensor[0]))
                    else:
                        sql_data_sensor = "SELECT measurevalue, timestamp FROM data WHERE (timestamp > '%s' and timestamp < '%s') and measuretype = '%s' and idsensor = %d;" % (
                            start_date_new, end_date_new, str(phenom), int(sensor[0]))
                    print sql_data_sensor
                    cur.execute(sql_data_sensor)
                    # sort tuples by time_pattern
                    sql_data = sorted(list(cur.fetchall()), key=lambda time: time[1])

                    for row in sql_data:
                        # http://stackoverflow.com/questions/16198606/python-linux-timestamp-to-date-time-and-reverse
                        # https://docs.python.org/2/library/datetime.html#strftime-strptime-behavior
                        time_index = int(time.mktime(time.strptime(str(row[1]), "%Y-%m-%d %H:%M:%S")) * 1000)
                        # some data do not have measurevalue (83k rows)
 
                        if row[0]:
                            value = float(row[0])
                        else:
                            value = 0.0
                        sensor_data[time_index] = value
                        
                    multi_iter1[sensor[0]] = sensor_data
                    # if there are no data
 
                    if multi_iter1[sensor[0]]:
                        vis = vincent.Line(multi_iter1[sensor[0]], width=600, height=200)
                        x_axis_str = 'data for sensor (' + str(sensor[0]) + '). Time period: ' + str(start_date_new) + ' to ' + str(end_date_new)
                        vis.axis_titles(x=str(x_axis_str), y=phenom_long)

                        vis._axis_properties(axis = 'y', title_size = 15, title_offset = -10,
                                 label_align = 'right', label_angle = 0, color = '#000000')
                        vis.scales['x'] = vincent.Scale(name = 'x', type = 'time', range = 'width',
                                            domain=vincent.DataRef(data = 'table', field = "data.idx"))
                        vis.scales['y'] = vincent.Scale(name = 'y', type = 'linear', range = 'height',
                                            domain=vincent.DataRef(data = 'table', field = "data.val"))

                        vis.to_json('static/vis_%s.json' % sensor[0])

                        popups.append(folium.Popup(max_width=1900).add_child(folium.Vega(json.load(open('static/vis_%s.json' % sensor[0])), width = "100%", height = "100%")))
                        
                        locations.append(sensor[1])
 
    if not locations:
        return flask.render_template('error.html', dates = dates, phenom = m_type, months = month, error = 'locations')
    holice_map.add_children(plugins.MarkerCluster(locations,popups))

    holice_map.save('templates/map.html')

    return flask.render_template('map.html')

if __name__ == '__main__':

    app.run(host="0.0.0.0", port = 80, threaded = True)#, debug = True)