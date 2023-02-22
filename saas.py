import requests
import json
from datetime import datetime
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/")
def home_page():
    return "<p><h2>KMA L2: Python Saas.</h2></p>"


@app.route(
    "/generate",
    methods=["POST"],
)
def get_weather():
    json_data = request.get_json()
    api_key = json_data.get("api_key")
    token = json_data.get("token")
    name = json_data.get("requester_name")
    location = json_data.get("location")
    date = json_data.get("date")
    time = json_data.get("time")


    url = 'https://api.opencagedata.com/geocode/v1/json'

    params = {
        'key': api_key,
        'q': location
    }
    response = requests.get(url, params=params).json()

    lat=""
    lng =""
    if response['results']:
        lat = response['results'][0]['geometry']['lat']
        lng = response['results'][0]['geometry']['lng']

    url = f"https://api.meteomatics.com/{date}T{time}/t_50m:C,wind_speed_10m:kmh,pressure_100m:Pa,absolute_humidity_2m:gm3,sunshine_duration_24h:p,prob_slippery_road_24h:p,prob_precip_24h:p/{lat},{lng}/json?access_token={token}"
    response = requests.get(url)

    data = response.json()

    res={}
    for key in data.keys():
        if key == "data":
            for elem in data[key]:
                for key in elem["coordinates"][0].keys():
                    if key == "dates":
                        for j in elem["coordinates"][0][key][0].keys():
                            if j == "value":
                                res[elem["parameter"]] = elem["coordinates"][0][key][0][j]


    utc_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    result = {
            "requester name": name,
            "timestamp": utc_time,
            "location": location,
            "date": date,
            "time": time,
            "weather":
                {
                    "Temp_c" : res['t_50m:C'],
                    "Wind_kph" : res['wind_speed_10m:kmh'],
                    "Pressure_mb" : res['pressure_100m:Pa'],
                    "Humidity" : res["absolute_humidity_2m:gm3"],
                    "Duration of sunshine from past 24 hours" : res["sunshine_duration_24h:p"],
                    'Probability for slippery roads in the last 24 hours in percent' : res["prob_slippery_road_24h:p"],
                    "Probability of precipitation in the previous 24h [%]" : res["prob_precip_24h:p"]

                }
    }
    return result
