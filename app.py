from flask import Flask, render_template, request, jsonify
import random

# ================= IMPORT SENSOR =================
try:
    from sensor import baca_suhu
except:
    def baca_suhu():
        return round(random.uniform(27, 32), 2)

app = Flask(__name__)

# ================= HALAMAN UTAMA =================
@app.route('/')
def index():
    return render_template('index.html')


# =================================================
# STATUS SUHU
# =================================================

def get_status(suhu):

    if 28 <= suhu <= 32:
        return "OPTIMAL"

    elif suhu < 28:
        return "TERLALU DINGIN"

    else:
        return "TERLALU PANAS"


# =================================================
# METODE LAMA
# RANDOM BIASA
# =================================================

def metode_lama(suhu_awal, waktu_total):

    suhu = suhu_awal
    data = []

    for t in range(waktu_total):

        # perubahan random
        suhu += random.uniform(-1.5, 1.5)

        data.append({
            "waktu": t,
            "suhu": round(suhu, 2),
            "status": get_status(suhu)
        })

    return data


# =================================================
# METODE BARU
# MOVING AVERAGE
# =================================================

def moving_average(data, window=3):

    hasil = []

    for i in range(len(data)):

        if i < window - 1:
            hasil.append(data[i])

        else:
            avg = sum(data[i-window+1:i+1]) / window
            hasil.append(avg)

    return hasil


def metode_baru_ma(suhu_awal, waktu_total):

    suhu = suhu_awal

    data_suhu = []
    hasil = []

    for t in range(waktu_total):

        # simulasi perubahan suhu
        suhu += random.uniform(-1.5, 1.5)

        data_suhu.append(suhu)

        # hitung moving average
        ma = moving_average(data_suhu)[-1]

        hasil.append({
            "waktu": t,
            "suhu": round(ma, 2),
            "status": get_status(ma)
        })

    return hasil


# =================================================
# ANALISIS PERBANDINGAN
# =================================================

def hitung_fluktuasi(data):

    total = 0

    for i in range(1, len(data)):

        selisih = abs(data[i]["suhu"] - data[i-1]["suhu"])
        total += selisih

    return round(total / len(data), 2)


# =================================================
# PERBANDINGAN METODE
# =================================================

@app.route('/compare', methods=['POST'])
def compare():

    # ================= INPUT SUHU =================

    if request.form.get('suhu'):

        suhu_awal = float(request.form['suhu'])
        sumber = "MANUAL"

    else:

        suhu_awal = baca_suhu()
        sumber = "SENSOR"

    waktu = int(request.form['waktu'])

    # ================= METODE =================

    metode1 = metode_lama(suhu_awal, waktu)
    metode2 = metode_baru_ma(suhu_awal, waktu)

    # ================= ANALISIS =================

    fluktuasi_lama = hitung_fluktuasi(metode1)
    fluktuasi_baru = hitung_fluktuasi(metode2)

    if fluktuasi_baru < fluktuasi_lama:
        kesimpulan = "Moving Average lebih stabil"
    else:
        kesimpulan = "Metode lama lebih stabil"

    return jsonify({

        "sumber_suhu": sumber,
        "suhu_awal": suhu_awal,

        "metode_lama": metode1,
        "metode_baru": metode2,

        "analisis": {
            "fluktuasi_metode_lama": fluktuasi_lama,
            "fluktuasi_moving_average": fluktuasi_baru,
            "kesimpulan": kesimpulan
        }
    })


# =================================================
# REALTIME
# =================================================

@app.route('/realtime')
def realtime():

    suhu = baca_suhu()

    data = []

    for t in range(50):

        suhu += random.uniform(-1, 1)

        data.append({
            "waktu": t,
            "suhu": round(suhu, 2),
            "status": get_status(suhu)
        })

    return jsonify(data)


# =================================================
# RUN SERVER
# =================================================

if __name__ == '__main__':
    app.run(debug=True)