from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)


# =========================
# HALAMAN UTAMA
# =========================
@app.route("/")
def index():
    return render_template("index.html")


# =========================
# SIMULASI NORMAL
# =========================
@app.route("/simulate", methods=["POST"])
def simulate():
    suhu_lingkungan = float(request.form["suhu"])
    waktu_total = int(request.form["waktu"])

    data = []
    suhu_internal = 30  # suhu awal tangki

    for t in range(waktu_total + 1):

        # perpindahan panas sederhana
        suhu_internal += 0.05 * (suhu_lingkungan - suhu_internal)

        # panas fermentasi aktif
        if 24 <= t <= 72:
            suhu_internal += 0.02

        # event diskrit
        if t == 20:
            suhu_internal -= 2   # penambahan nira

        if t == 50:
            suhu_internal += 3   # fermentasi puncak

        # status suhu
        if 28 <= suhu_internal <= 32:
            status = "OPTIMAL"
        elif suhu_internal < 28:
            status = "TERLALU DINGIN"
        else:
            status = "TERLALU PANAS"

        data.append({
            "waktu": t,
            "suhu": round(suhu_internal, 2),
            "status": status
        })

    return jsonify(data)


# =========================
# MODE SENSOR REAL-TIME
# =========================
@app.route("/realtime")
def realtime():
    data = []

    suhu_lingkungan = 30
    suhu_internal = 30

    for t in range(100):

        # pengaruh lingkungan
        suhu_internal += 0.05 * (suhu_lingkungan - suhu_internal)

        # panas fermentasi
        if 20 <= t <= 60:
            suhu_internal += 0.03

        # noise sensor agar realistis
        suhu_internal += random.uniform(-0.3, 0.3)

        # status
        if 28 <= suhu_internal <= 32:
            status = "OPTIMAL"
        elif suhu_internal < 28:
            status = "TERLALU DINGIN"
        else:
            status = "TERLALU PANAS"

        data.append({
            "waktu": t,
            "suhu": round(suhu_internal, 2),
            "status": status
        })

    return jsonify(data)


# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    app.run(debug=True)