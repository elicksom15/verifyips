from flask import Flask, render_template, request, session, jsonify
import threading
import requests
import time

app = Flask(__name__)
app.secret_key = "supersecretkey"

target_url = "http://www.bixopix.com/bingo/venda_bilhetes.php"
headers = {
    "X-Requested-With": "XMLHttpRequest",
    "Accept-Language": "pt-BR,pt;q=0.9",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/134.0.0.0 Safari/537.36",
    "Origin": "http://www.bixopix.com",
    "Referer": "http://www.bixopix.com/bingo/bingo2.php?udln=100-1&v=2.00",
}

running = False

def send_request():
    global running
    while running:
        if "phpsessid" in session:
            cookies = {"PHPSESSID": session["phpsessid"]}
            data = {
                "functionname": "",
                "arguments[]": session["game_time"],
                "arguments[]": "0.0001"
            }
            try:
                response = requests.post(target_url, headers=headers, cookies=cookies, data=data)
                print("Response:", response.text)
            except Exception as e:
                print("Error:", str(e))
        time.sleep(0.5)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        session["game_time"] = request.form["game_time"]
        session["phpsessid"] = request.form["phpsessid"]
        return jsonify({"status": "Session saved"})
    return render_template("index.html")

@app.route("/start", methods=["POST"])
def start():
    global running
    if not running:
        running = True
        thread = threading.Thread(target=send_request)
        thread.daemon = True
        thread.start()
    return jsonify({"status": "Started"})

@app.route("/stop", methods=["POST"])
def stop():
    global running
    running = False
    return jsonify({"status": "Stopped"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8181)

# index.html
index_html = """
<!DOCTYPE html>
<html lang='pt-br'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>Bingo Automático</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 20px; }
        input, button { margin: 10px; padding: 10px; font-size: 16px; }
    </style>
</head>
<body>
    <h1>Bingo Automático</h1>
    <form id='configForm'>
        <label>Horário do Jogo:</label>
        <input type='text' id='game_time' placeholder='2025-03-30 13:00:00'><br>
        <label>PHPSESSID:</label>
        <input type='text' id='phpsessid' placeholder='Digite seu PHPSESSID'><br>
        <button type='button' onclick='saveConfig()'>Salvar Configuração</button>
    </form>
    <button onclick='start()'>Iniciar</button>
    <button onclick='stop()'>Parar</button>
    <script>
        function saveConfig() {
            fetch('/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({
                    game_time: document.getElementById('game_time').value,
                    phpsessid: document.getElementById('phpsessid').value
                })
            }).then(response => response.json()).then(data => alert(data.status));
        }
        function start() {
            fetch('/start', { method: 'POST' }).then(response => response.json()).then(data => alert(data.status));
        }
        function stop() {
            fetch('/stop', { method: 'POST' }).then(response => response.json()).then(data => alert(data.status));
        }
    </script>
</body>
</html>
"""

with open("templates/index.html", "w", encoding="utf-8") as f:
    f.write(index_html)
