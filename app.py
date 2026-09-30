from flask import Flask, request, jsonify, send_from_directory, render_template
import os
import sqlite3
from werkzeug.utils import secure_filename

from database import (
    veritabani_olustur,
    calisma_ekle,
    ogrenci_ekle,
    ogrencileri_getir
)

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
DATABASE = "detay_sanat.db"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

veritabani_olustur()

@app.route("/ogrenci-giris")
def ogrenci_giris():
    return render_template("ogrenci_giris.html")
@app.route("/ogrenci-panel")
def ogrenci_panel():

    return render_template(
        "ogrenci_panel.html"
    )
@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/ogretmen")
def ogretmen():
    return send_from_directory(".", "ogretmen.html")


@app.route("/sonuclar")
def sonuclar():
    return send_from_directory(".", "sonuclar.html")


@app.route("/degerlendir/<int:id>")
def degerlendir(id):
    return send_from_directory(".", "degerlendir.html")


@app.route("/uploads/<filename>")
def uploads(filename):
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )


# --------------------------------------------------
# ÖĞRENCİ EKLE
# --------------------------------------------------

@app.route("/ogrenci-ekle", methods=["POST"])
def ogrenci_ekle_api():

    veri = request.get_json()

    if not veri:
        return jsonify({
            "basarili": False,
            "mesaj": "Veri alınamadı."
        })

    ogrenci_kodu = veri.get(
        "ogrenci_kodu",
        ""
    ).strip().upper()

    ad_soyad = veri.get(
        "ad_soyad",
        ""
    ).strip()

    if not ogrenci_kodu:
        return jsonify({
            "basarili": False,
            "mesaj": "Öğrenci kodu girilmedi."
        })

    if not ad_soyad:
        return jsonify({
            "basarili": False,
            "mesaj": "Ad soyad girilmedi."
        })

    try:
        ogrenci_ekle(
            ogrenci_kodu,
            ad_soyad
        )

        return jsonify({
            "basarili": True,
            "mesaj": "Öğrenci başarıyla eklendi."
        })

    except Exception as e:

        return jsonify({
            "basarili": False,
            "mesaj": f"Öğrenci eklenemedi: {str(e)}"
        })


# --------------------------------------------------
# ÖĞRENCİLERİ GETİR
# --------------------------------------------------

@app.route("/ogrenciler")
def ogrenciler():

    kayitlar = ogrencileri_getir()

    liste = []

    for kayit in kayitlar:

        liste.append({
            "id": kayit["id"],
            "ogrenci_kodu": kayit["ogrenci_kodu"],
            "ad_soyad": kayit["ad_soyad"]
        })

    return jsonify(liste)


# --------------------------------------------------
# ÇALIŞMA GÖNDER
# --------------------------------------------------

@app.route("/gonder", methods=["POST"])
def gonder():

    ogrenci_kodu = request.form.get(
        "ogrenci_kodu",
        ""
    ).strip().upper()

    calisma_turu = request.form.get(
        "calisma_turu"
    )

    fotograf = request.files.get(
        "fotograf"
    )

    if not ogrenci_kodu:
        return jsonify({
            "basarili": False,
            "mesaj": "Öğrenci kodu girilmedi."
        })

    if not fotograf:
        return jsonify({
            "basarili": False,
            "mesaj": "Çizim fotoğrafı gönderilmedi."
        })

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            ogrenci_kodu,
            ad_soyad
        FROM ogrenciler
        WHERE ogrenci_kodu = ?
    """, (ogrenci_kodu,))

    ogrenci = cursor.fetchone()

    conn.close()

    if not ogrenci:
        return jsonify({
            "basarili": False,
            "mesaj": "Bu öğrenci kodu kayıtlı değil."
        })

    ogrenci_adi = ogrenci["ad_soyad"]

    dosya_adi = secure_filename(
        fotograf.filename
    )

    import time

    zaman = int(time.time())

    yeni_dosya_adi = (
        f"{zaman}_{dosya_adi}"
    )

    dosya_yolu = os.path.join(
        app.config["UPLOAD_FOLDER"],
        yeni_dosya_adi
    )

    fotograf.save(dosya_yolu)

    calisma_id = calisma_ekle(
        ogrenci_adi,
        calisma_turu,
        yeni_dosya_adi,
        ogrenci_kodu
    )

    print()
    print("Yeni öğrenci çalışması geldi!")
    print("-----------------------------")
    print("ID:", calisma_id)
    print("Öğrenci kodu:", ogrenci_kodu)
    print("Öğrenci:", ogrenci_adi)
    print("Çalışma:", calisma_turu)
    print("Fotoğraf:", yeni_dosya_adi)
    print("-----------------------------")
    print()

    return jsonify({
        "basarili": True,
        "mesaj": "Çizimin başarıyla gönderildi.",
        "id": calisma_id
    })


# --------------------------------------------------
# ÇALIŞMALAR
# --------------------------------------------------

@app.route("/calismalar")
def calismalar():

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM calismalar
        ORDER BY id DESC
    """)

    kayitlar = cursor.fetchall()

    conn.close()

    liste = []

    for kayit in kayitlar:

        liste.append({
            "id": kayit["id"],
            "ogrenci_adi": kayit["ogrenci_adi"],
            "ogrenci_kodu": kayit["ogrenci_kodu"],
            "calisma_turu": kayit["calisma_turu"],
            "fotograf": kayit["fotograf"],
            "durum": kayit["durum"],
            "tarih": kayit["tarih"]
        })

    return jsonify(liste)


# --------------------------------------------------
# ÖĞRENCİ SONUÇLARI
# --------------------------------------------------

@app.route("/ogrenci-sonuclari/<ogrenci_kodu>")
def ogrenci_sonuclari(ogrenci_kodu):

    ogrenci_kodu = (
        ogrenci_kodu
        .strip()
        .upper()
    )

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            ogrenci_kodu,
            ad_soyad
        FROM ogrenciler
        WHERE ogrenci_kodu = ?
    """, (ogrenci_kodu,))

    ogrenci = cursor.fetchone()

    if not ogrenci:

        conn.close()

        return jsonify({
            "basarili": False,
            "mesaj": "Öğrenci bulunamadı."
        }), 404

    cursor.execute("""
        SELECT
            id,
            calisma_turu,
            durum,
            kompozisyon,
            oran_oranti,
            perspektif,
            isik_golge,
            cizgi_kullanimi,
            yorum,
            tarih
        FROM calismalar
        WHERE ogrenci_kodu = ?
        ORDER BY id DESC
    """, (ogrenci_kodu,))

    calisma_kayitlari = cursor.fetchall()

    conn.close()

    liste = []

    for calisma in calisma_kayitlari:

        puanlar = [
            calisma["kompozisyon"],
            calisma["oran_oranti"],
            calisma["perspektif"],
            calisma["isik_golge"],
            calisma["cizgi_kullanimi"]
        ]

        if all(
            puan is not None
            for puan in puanlar
        ):
            toplam = sum(puanlar)
        else:
            toplam = None

        liste.append({
            "id": calisma["id"],
            "calisma_turu": calisma["calisma_turu"],
            "durum": calisma["durum"],
            "kompozisyon": calisma["kompozisyon"],
            "oran_oranti": calisma["oran_oranti"],
            "perspektif": calisma["perspektif"],
            "isik_golge": calisma["isik_golge"],
            "cizgi_kullanimi": calisma["cizgi_kullanimi"],
            "toplam": toplam,
            "yorum": calisma["yorum"],
            "tarih": calisma["tarih"]
        })

    return jsonify({
        "basarili": True,
        "ogrenci": {
            "ogrenci_kodu": ogrenci["ogrenci_kodu"],
            "ad_soyad": ogrenci["ad_soyad"]
        },
        "calismalar": liste
    })


# --------------------------------------------------
# TEK ÇALIŞMA
# --------------------------------------------------

@app.route("/calisma/<int:id>")
def calisma(id):

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM calismalar
        WHERE id = ?
    """, (id,))

    kayit = cursor.fetchone()

    conn.close()

    if not kayit:
        return jsonify({
            "basarili": False,
            "mesaj": "Çalışma bulunamadı."
        }), 404

    return jsonify({
        "id": kayit["id"],
        "ogrenci_adi": kayit["ogrenci_adi"],
        "calisma_turu": kayit["calisma_turu"],
        "fotograf": kayit["fotograf"],
        "durum": kayit["durum"]
    })


# --------------------------------------------------
# DEĞERLENDİRME KAYDET
# --------------------------------------------------

@app.route(
    "/degerlendirme-kaydet",
    methods=["POST"]
)
def degerlendirme_kaydet():

    try:

        veri = request.get_json()

        print()
        print("DEĞERLENDİRME İSTEĞİ GELDİ")
        print("Gelen veri:", veri)

        if not veri:
            return jsonify({
                "basarili": False,
                "mesaj": "Veri alınamadı."
            }), 400

        try:
            calisma_id = int(
                veri.get("id")
            )
        except (TypeError, ValueError):

            return jsonify({
                "basarili": False,
                "mesaj": "Çalışma ID geçersiz."
            }), 400

        try:

            kompozisyon = int(
                veri.get("kompozisyon")
            )

            oran_oranti = int(
                veri.get("oran_oranti")
            )

            perspektif = int(
                veri.get("perspektif")
            )

            isik_golge = int(
                veri.get("isik_golge")
            )

            cizgi_kullanimi = int(
                veri.get("cizgi_kullanimi")
            )

        except (TypeError, ValueError):

            return jsonify({
                "basarili": False,
                "mesaj": "Puanlardan biri geçersiz."
            }), 400

        yorum = str(
            veri.get("yorum", "")
        ).strip()

        gecerli_puanlar = [5, 10, 15, 20]

        for puan in [
            kompozisyon,
            oran_oranti,
            perspektif,
            isik_golge,
            cizgi_kullanimi
        ]:

            if puan not in gecerli_puanlar:

                return jsonify({
                    "basarili": False,
                    "mesaj": "Geçersiz puan gönderildi."
                }), 400

        toplam = (
            kompozisyon
            + oran_oranti
            + perspektif
            + isik_golge
            + cizgi_kullanimi
        )

        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id,
                fotograf,
                durum
            FROM calismalar
            WHERE id = ?
        """, (calisma_id,))

        kayit = cursor.fetchone()

        if not kayit:

            conn.close()

            return jsonify({
                "basarili": False,
                "mesaj": "Çalışma bulunamadı."
            }), 404

        fotograf = kayit["fotograf"]

        print(
            "Bulunan çalışma:",
            dict(kayit)
        )

        cursor.execute("""
            UPDATE calismalar
            SET
                kompozisyon = ?,
                oran_oranti = ?,
                perspektif = ?,
                isik_golge = ?,
                cizgi_kullanimi = ?,
                yorum = ?,
                durum = ?
            WHERE id = ?
        """, (
            kompozisyon,
            oran_oranti,
            perspektif,
            isik_golge,
            cizgi_kullanimi,
            yorum,
            "Değerlendirildi",
            calisma_id
        ))

        degisen_satir = cursor.rowcount

        conn.commit()

        cursor.execute("""
            SELECT
                id,
                durum,
                kompozisyon,
                oran_oranti,
                perspektif,
                isik_golge,
                cizgi_kullanimi,
                yorum
            FROM calismalar
            WHERE id = ?
        """, (calisma_id,))

        kontrol = cursor.fetchone()

        conn.close()

        print()
        print("UPDATE sonucu:", degisen_satir)

        if kontrol:
            print(
                "Güncel kayıt:",
                dict(kontrol)
            )

        print()

        if not kontrol:

            return jsonify({
                "basarili": False,
                "mesaj": "Kayıt güncellendi ancak tekrar okunamadı."
            }), 500

        if kontrol["durum"] != "Değerlendirildi":

            return jsonify({
                "basarili": False,
                "mesaj": "Değerlendirme kaydedilemedi."
            }), 500

        # Fotoğrafı sil
        if fotograf:

            dosya_yolu = os.path.join(
                app.config["UPLOAD_FOLDER"],
                fotograf
            )

            if os.path.exists(dosya_yolu):

                try:

                    os.remove(dosya_yolu)

                    print(
                        "Değerlendirilen fotoğraf silindi:",
                        fotograf
                    )

                except Exception as e:

                    print(
                        "Fotoğraf silinemedi:",
                        str(e)
                    )

        print()
        print("DEĞERLENDİRME BAŞARIYLA KAYDEDİLDİ")
        print("Çalışma ID:", calisma_id)
        print("Toplam puan:", toplam)
        print()

        return jsonify({
            "basarili": True,
            "mesaj": "Değerlendirme başarıyla kaydedildi.",
            "toplam": toplam
        })

    except Exception as e:

        print()
        print("DEĞERLENDİRME HATASI:")
        print(str(e))
        print()

        return jsonify({
            "basarili": False,
            "mesaj": f"Sunucu hatası: {str(e)}"
        }), 500


# --------------------------------------------------
# SUNUCU
# --------------------------------------------------

if __name__ == "__main__":

    print(
        "DETAY SANAT AKADEMİ sunucusu başlıyor..."
    )

    print(
        "Bilgisayardan: "
        "http://127.0.0.1:5000"
    )

    print(
        "Telefondan: "
        "http://192.168.0.18:5000"
    )

    print(
        "Öğretmen Paneli: "
        "http://127.0.0.1:5000/ogretmen"
    )

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )