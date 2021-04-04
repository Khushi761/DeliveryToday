from typing import List
import requests

url = "https://postcodes.io/postcodes"    #url to get all the postcodes, calling an API, app on the internet where we make post request and give it buunch of postcodes

EARTH_RADIUS_IN_MILES = 3958.761

def get_distance(postcodes: List):  #pass the list of postcodes that user gives
    postcodes = {"postcodes" : postcodes} #dictionary created with field called 'postcodes' which is now referred to a postcodes, (postcodes entered by user)
    res = requests.post(url, data = postcodes).json() #{} dictionary [] list
    if len(res["result"]) < 2:     #if the postcodes the user enters are less thean 2
        return None
    source = (res["result"][0]["result"]["latitude"], res["result"][0]["result"]["longitude"])  #go to result then 0 (frist value of what user enters))
    destination = (res["result"][1]["result"]["latitude"], res["result"][1]["result"]["longitude"])
    lat_a = radian(source[0])
    lat_b = radians(destination[0])
    long_diff = radians(source[1] - destination[1])
    distance = (sin(lat_a) * sin(lat_b) + cos(lat_a) * cos(lat_b) * cos(long_diff) )
    return acos(distance) * EARTH_RADIUS_IN_MILES
    
    #Minimum viable product (MVP)

def get_address(postcode: str):
    res = requests.get(url+f"/{postcode}").json()["result"]
    return f"{postcode}, {res['parish']}, {res['admin_district']}, {res['admin_ward']}"