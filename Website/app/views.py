from __future__ import print_function
import datetime
import sys

from app import app
from flask import render_template, request, jsonify

from Database import backend


@app.route('/', methods=['GET', 'POST'])
def index():

    return render_template('index.html')

@app.route('/api', methods=['POST'])
def api_port():
    post_data = request.get_json()
    print(post_data, file=sys.stderr)

    home = post_data['home_gps']
    home_lat = home['lat']  # it has gps data
    home_lng = home['lng']

    txtSearch = post_data['search_text']
    current_time = datetime.datetime.now()
    ctime = str(current_time.year) + "-" + str(current_time.month) + "-" + str(current_time.day) + "|" + str(current_time.hour) + ":" +str(current_time.minute) + ":" + str(current_time.second)
    # search_option = post_data['search_option']
    # print(search_option, file=sys.stderr)



    # resultAna = ut.get_destinations(home_lat, home_lng, txtSearch, search_option)
    resultAna = backend.get_destinations(home_lat, home_lng, txtSearch, ctime) # yyyy-mm-dd|hh:mm:ss


    # target_lat, target_lng = google(txtSearch)
    #
    #
    # stops = {}
    # lat = target_lat
    # lng = target_lng
    # for i in range(0,5):
    #     lat = lat + 0.01
    #     lng = lng + 0.01
    #     stops[str(i)] = {'lat': lat,
    #             'lng': lng,
    #             'title': str(i),
    #             'description': str(i),
    #             'path':[{'lat': home_lat, 'lng': home_lng},
    #                     {'lat': home_lat+0.03, 'lng': home_lng},
    #                     {'lat': lat, 'lng': lng}]}
    #
    # # print(search_target, file=sys.stderr)
    # # print(home_lat,home_lng, file=sys.stderr)
    #
    # data={}
    # data['stops']=stops
    # data['shape']=get_shape()

    # return jsonify(**data)

    return jsonify(**resultAna)
