import csv
import os

def simulasi(T_awal, T_lingkungan, waktu):
    # Parameter fisik
    k = 16        # konduktivitas SS-304
    A = 1.2       # luas permukaan (m2)
    m = 100       # massa nira (kg)
    c = 4180      # kalor jenis nira (J/kgC)

    T = T_awal
    hasil = []

    os.makedirs("data", exist_ok=True)

    with open("data/hasil_simulasi.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Jam", "Suhu", "Status"])

        for t in range(waktu):
            # Persamaan termodinamika
            T = T + (k * A / (m * c)) * (T_lingkungan - T)

            # Event diskrit: status fermentasi
            if 28 <= T <= 32:
                status = "OPTIMAL"
            elif T < 28:
                status = "TERLALU DINGIN"
            else:
                status = "TERLALU PANAS"

            hasil.append({
                "waktu": t,
                "suhu": round(T, 2),
                "status": status
            })

            writer.writerow([t, round(T, 2), status])

    return hasil