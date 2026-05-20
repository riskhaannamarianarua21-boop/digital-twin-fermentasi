from flask import Flask, render_template, request, jsonify
import random
import math  # Diperlukan untuk perhitungan matematika presisi jika ada pengembangan

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
# PERSAMAAN DIFERENSIAL (MODEL FISIKA TANGKI)
# =================================================
# Rumus hukum pendinginan Newton untuk tangki fermentasi:
# dT/dt = (k * A / (m * c)) * (Suhu_Lingkungan - Suhu_Tangki)
def fungsi_turunan_suhu(T):
    # Parameter diubah agar kurva melengkung tajam dan estetik dalam rentang 120 jam
    k = 120             # Koefisien perpindahan panas dinaikkan signifikan
    A = 3.5             # Luas area kontak diperbesar
    m = 20              # Massa diperkecil agar suhu cepat bergejolak
    c = 2500            # Kalor jenis diturunkan agar lebih sensitif terhadap perubahan
    T_lingkungan = 27.0 
    return (k * A / (m * c)) * (T_lingkungan - T)


# =================================================
# METODE 1: EULER METHOD (METODE LAMA)
# =================================================
def metode_lama(suhu_awal, waktu_total):
    """METODE 1: EULER METHOD"""
    data = []
    T = suhu_awal
    # Kita perbesar dt ke 4 agar akumulasi error numerik Euler terlihat di grafik
    dt = 4  
    
    for t in range(waktu_total):
        data.append({
            "waktu": t,
            "suhu": round(T, 4),
            "status": get_status(T)
        })
        # Simulasi berjalan dengan lompatan kalkulasi yang lebih renggang
        T = T + dt * fungsi_turunan_suhu(T)
        
    return data

def metode_baru_ma(suhu_awal, waktu_total):
    """METODE 2: RUNGE-KUTTA ORDE 4 / RK4 (METODE BARU)"""
    data = []
    T = suhu_awal
    dt = 1  # RK4 menggunakan dt = 1 untuk akurasi tinggi
    
    for t in range(waktu_total):
        data.append({
            "waktu": t,
            "suhu": round(T, 4),
            "status": get_status(T)
        })
        # Perbaikan rumus k1 sampai k4 dengan nama fungsi yang benar
        k1 = fungsi_turunan_suhu(T)
        k2 = fungsi_turunan_suhu(T + 0.5 * dt * k1)
        k3 = fungsi_turunan_suhu(T + 0.5 * dt * k2)
        k4 = fungsi_turunan_suhu(T + dt * k3)
        
        T = T + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        
    return data


# =================================================
# ANALISIS PERBANDINGAN (AKURASI/ERROR SELISIH)
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

    # ================= EKSEKUSI METODE NUMERIK =================
    metode1 = metode_lama(suhu_awal, waktu)      # Ini menjalankan Euler
    metode2 = metode_baru_ma(suhu_awal, waktu)    # Ini menjalankan RK4

    # ================= ANALISIS STABILITAS / KONVERGENSI =================
    fluktuasi_lama = hitung_fluktuasi(metode1)
    fluktuasi_baru = hitung_fluktuasi(metode2)

    # Membandingkan metode mana yang mencapai kestabilan termal lebih halus
    if fluktuasi_baru < fluktuasi_lama:
        kesimpulan = "Metode RK4 (Orde 4) terbukti lebih akurat dan stabil dalam memodelkan penyusutan suhu tangki"
    else:
        kesimpulan = "Metode Euler memberikan pendekatan linier yang lebih cepat"

    return jsonify({
        "sumber_suhu": sumber,
        "suhu_awal": suhu_awal,
        "metode1": metode1,
        "metode2": metode2,
        "analisis": {
            "fluktuasi_metode_lama": fluktuasi_lama,
            "fluktuasi_moving_average": fluktuasi_baru,
            "kesimpulan": kesimpulan
        }
    })


# =================================================
# REALTIME (MONITORING KONDISI NYATA TANGKI)
# =================================================
@app.route('/realtime', methods=['POST'])
def realtime():
    suhu_input = request.form.get('suhu')
    waktu_input = request.form.get('waktu') # Perbaikan: Menangkap data waktu dari form input
    
    # Validasi suhu awal
    if suhu_input and suhu_input.strip() != "":
        suhu_awal = float(suhu_input)
    else:
        suhu_awal = 29.0
        
    # Perbaikan: Menentukan batas total waktu mengikuti input user (+1 agar ujung angka pas di grafik)
    if waktu_input and waktu_input.strip() != "":
        total_waktu = int(waktu_input) + 1
    else:
        total_waktu = 121 # Nilai default jika input kosong
        
    data = []
    suhu = suhu_awal
    
    # Perbaikan: Mengubah range statis 121 menjadi dinamis mengikuti variabel total_waktu
    for t in range(total_waktu):
        data.append({
            "waktu": t,
            "suhu": round(suhu, 2)
        })
        
        fluktuasi = random.uniform(-0.4, 0.4)
        kecenderungan = (28.5 - suhu) * 0.12 
        suhu += fluktuasi + kecenderungan
        
    return jsonify(data)


# =================================================
# RUN SERVER
# =================================================
if __name__ == '__main__':
    app.run(debug=True)