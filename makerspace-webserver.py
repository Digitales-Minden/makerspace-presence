from flask import Flask
from flask import jsonify
import time

app = Flask(__name__)

@app.route("/")
def show_time_list():
    html = "<html><body><table>"
    activity_file = open("/home/fabian/Programmierung/Python/makerspace-presence/test.csv", "r")
    for line in activity_file:
        line_information = line.split(";")
        html += "<tr><td>" + line_information[0] + "</td><td>" +line_information[1] + "</td></tr>"
        
    html += "</table></body></html>"
    return html

@app.route("/devices/current")
def show_devices_count():
    return """
    <p>Geschafft!</p>
    """

if __name__ == "__main__":
    app.run()
