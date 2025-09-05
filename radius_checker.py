import math
from flask import Flask, request, render_template_string
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

app = Flask(__name__)

# Base location: Asheville, NC
BASE_ADDRESS = "Asheville, NC"
BASE_COORDS = None

# Initialize geolocator
geolocator = Nominatim(user_agent="radius_checker")

# Get base coordinates once
location = geolocator.geocode(BASE_ADDRESS)
if location:
    BASE_COORDS = (location.latitude, location.longitude)

# Radius in miles
RADIUS_MILES = 15

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Radius Checker</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #2c3e50; }
        input[type=text] { width: 300px; padding: 8px; }
        input[type=submit] { padding: 8px 16px; margin-left: 8px; }
        .result { margin-top: 20px; font-size: 18px; font-weight: bold; }
        .inside { color: green; }
        .outside { color: red; }
    </style>
</head>
<body>
    <h1>15-Mile Radius Checker (Asheville, NC)</h1>
    <form method="get" action="/check_address">
        <input type="text" name="address" placeholder="Enter property address" required>
        <input type="submit" value="Check">
    </form>
    {% if result %}
        <div class="result {{ 'inside' if result.within else 'outside' }}">
            Address: {{ result.address }}<br>
            Distance: {{ result.distance }} miles<br>
            Status: {{ result.status }}
        </div>
    {% endif %}
</body>
</html>
"""

@app.route("/check_address", methods=["GET"])
def check_address():
    address = request.args.get("address")
    result = None

    if address:
        try:
            loc = geolocator.geocode(address)
            if loc:
                prop_coords = (loc.latitude, loc.longitude)
                distance_miles = geodesic(BASE_COORDS, prop_coords).miles
                within_radius = distance_miles <= RADIUS_MILES
                result = {
                    "address": address,
                    "distance": round(distance_miles, 2),
                    "within": within_radius,
                    "status": "INSIDE" if within_radius else "OUTSIDE"
                }
            else:
                result = {"address": address, "distance": "N/A", "within": False, "status": "Address not found"}
        except Exception as e:
            result = {"address": address, "distance": "N/A", "within": False, "status": f"Error: {e}"}

    return render_template_string(HTML_TEMPLATE, result=result)

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, result=None)

if __name__ == "__main__":
    app.run(debug=True)
