from flask import Flask, render_template, request, session
import threading
import time
import requests

app = Flask(__name__)
app.secret_key = "supersecretkey"

running = False

def send_request(phpsessid, horario, data):
    global running
    while running:
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Cookie": f"PHPSESSID={phpsessid}"
        }
        payload = {
            "functionname": "",
            "arguments[]": f"{data} {horario}",
            "arguments[]": "0.0001"
        }
        response = requests.post("http://www.bixopix.com/bingo/venda_bilhetes.php", headers=headers, data=payload)
        print(response.text)
        time.sleep(0.5)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start", methods=["POST"])
def start():
    global running
    if not running:
        running = True
        phpsessid = request.form.get("phpsessid")
        horario = request.form.get("horario")
        data = request.form.get("data")
        session["phpsessid"] = phpsessid
        threading.Thread(target=send_request, args=(phpsessid, horario, data)).start()
    return "Iniciado!"

@app.route("/stop", methods=["POST"])
def stop():
    global running
    running = False
    return "Parado!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8181, debug=True)
