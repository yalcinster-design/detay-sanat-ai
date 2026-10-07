from flask import (
    Flask,
    request,
    jsonify,
    send_from_directory,
    render_template,
    render_template_string,
    session,
    redirect,
    url_for
)

import os
import sqlite3
import time
from functools import wraps
from werkzeug.utils import secure_filename

from database import (
    veritabani_olustur,
    calisma_ekle,
    ogrenci_ekle,
    ogrencileri_getir
)


# =========================================================
# AYARLAR
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "local-development-secret-key"
)

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
DATABASE = os.path.join(BASE_DIR, "detay_sanat.db")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

veritabani_olustur()


# =========================================================
# YÖNETİCİ KONTROLÜ
# =========================================================

def yonetici_gerekli(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if not session.get("yonetici_giris"):
            return jsonify({
                "basarili": False,
                "mesaj": "Yönetici girişi gerekli."
            }), 401

        return f(*args, **kwargs)

    return decorated_function


# =========================================================
# ANA SAYFA
# =========================================================

@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")


# =========================================================
# ÖĞRENCİ GİRİŞ
# =========================================================

@app.route("/ogrenci-giris")
def ogrenci_giris():
    return render_template("ogrenci_giris.html")


# =========================================================
# ÖĞRENCİ PANEL
# =========================================================

@app.route("/ogrenci-panel")
def ogrenci_panel():
    return render_template("ogrenci_panel.html")


# =========================================================
# SONUÇLAR SAYFASI
# =========================================================

@app.route("/sonuclar")
def sonuclar():

    try:

        dosya_yolu = os.path.join(
            BASE_DIR,
            "sonuclar.html"
        )

        with open(
            dosya_yolu,
            "r",
            encoding="utf-8"
        ) as dosya:

            html = dosya.read()

        ana_menu_butonu = """
        <a href="/"
           style="
               position: fixed;
               top: 15px;
               left: 15px;
               z-index: 9999;
               display: inline-block;
               padding: 12px 18px;
               background: #222;
               color: white;
               text-decoration: none;
               border-radius: 10px;
               font-family: Arial, sans-serif;
               font-size: 14px;
               box-shadow: 0 3px 10px rgba(0,0,0,0.20);
           ">
            ← Ana Menü
        </a>
        """

        if "</body>" in html:

            html = html.replace(
                "</body>",
                ana_menu_butonu + "</body>"
            )

        else:

            html += ana_menu_butonu

        return html

    except Exception as e:

        return f"""
        <!DOCTYPE html>
        <html lang="tr">
        <head>
            <meta charset="UTF-8">

            <meta
                name="viewport"
                content="width=device-width, initial-scale=1.0"
            >

            <title>Hata</title>
        </head>

        <body
            style="
                font-family: Arial;
                text-align: center;
                padding: 40px;
            "
        >

            <h2>Sonuçlar sayfası açılamadı.</h2>

            <p>{str(e)}</p>

            <p>
                <a href="/">← Ana Menü</a>
            </p>

        </body>
        </html>
        """, 500


# =========================================================
# YÖNETİCİ GİRİŞİ
# =========================================================

@app.route(
    "/yonetici-giris",
    methods=["GET", "POST"]
)
def yonetici_giris():

    if request.method == "POST":

        sifre = request.form.get("sifre", "")

        if sifre == ADMIN_PASSWORD:

            session["yonetici_giris"] = True

            return redirect(
                url_for("yonetici_panel")
            )

        return """
        <!DOCTYPE html>
        <html lang="tr">
        <head>
            <meta charset="UTF-8">
            <meta
                name="viewport"
                content="width=device-width, initial-scale=1.0"
            >
            <title>Hatalı Şifre</title>
        </head>

        <body
            style="
                font-family: Arial;
                text-align: center;
                padding: 40px;
            "
        >

            <h2>Şifre hatalı.</h2>

            <p>
                <a href="/yonetici-giris">
                    Tekrar dene
                </a>
            </p>

        </body>
        </html>
        """, 401

    return """
    <!DOCTYPE html>
    <html lang="tr">

    <head>

        <meta charset="UTF-8">

        <meta
            name="viewport"
            content="width=device-width, initial-scale=1.0"
        >

        <title>Yönetici Girişi</title>

        <style>

            * {
                box-sizing: border-box;
            }

            body {
                margin: 0;
                background: #f4f4f4;
                font-family: Arial, sans-serif;
            }

            .container {
                width: 90%;
                max-width: 400px;
                margin: 80px auto;
                background: white;
                padding: 30px;
                border-radius: 16px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.10);
            }

            h1 {
                text-align: center;
                margin-bottom: 25px;
            }

            input {
                width: 100%;
                padding: 14px;
                border: 1px solid #ddd;
                border-radius: 10px;
                margin-bottom: 15px;
                font-size: 16px;
            }

            button {
                width: 100%;
                padding: 14px;
                border: none;
                border-radius: 10px;
                background: #222;
                color: white;
                font-size: 16px;
                cursor: pointer;
            }

            .home {
                display: block;
                text-align: center;
                margin-top: 20px;
                color: #555;
                text-decoration: none;
            }

        </style>

    </head>

    <body>

        <div class="container">

            <h1>🔐 Yönetici Girişi</h1>

            <form method="POST">

                <input
                    type="password"
                    name="sifre"
                    placeholder="Yönetici şifresi"
                    required
                >

                <button type="submit">
                    Giriş Yap
                </button>

            </form>

    </body>

    </html>
    """


# =========================================================
# YÖNETİCİ ÇIKIŞI
# =========================================================

@app.route("/yonetici-cikis")
def yonetici_cikis():

    session.clear()

    return redirect(
        url_for("home")
    )


# =========================================================
# YÖNETİCİ PANELİ
# =========================================================

@app.route("/yonetici-panel")
@yonetici_gerekli
def yonetici_panel():

    html = """
    <!DOCTYPE html>
    <html lang="tr">

    <head>

        <meta charset="UTF-8">

        <meta
            name="viewport"
            content="width=device-width, initial-scale=1.0"
        >

        <title>Yönetici Paneli</title>

        <style>

            * {
                box-sizing: border-box;
            }

            body {
                margin: 0;
                background: #f4f4f4;
                font-family: Arial, sans-serif;
            }

            .container {
                width: 92%;
                max-width: 700px;
                margin: 30px auto;
            }

            h1 {
                text-align: center;
                margin-bottom: 25px;
            }

            .menu {
                display: flex;
                flex-direction: column;
                gap: 12px;
            }

            button,
            .button {
                display: block;
                width: 100%;
                padding: 16px;
                border: none;
                border-radius: 12px;
                background: white;
                color: #222;
                text-decoration: none;
                font-size: 16px;
                cursor: pointer;
                box-shadow: 0 3px 12px rgba(0,0,0,0.08);
            }

            .danger {
                background: #222;
                color: white;
            }

            .student {
                background: white;
                padding: 15px;
                margin-top: 10px;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            }

            .student button {
                width: auto;
                display: inline-block;
                background: #222;
                color: white;
                margin-top: 10px;
            }

            input {
                width: 100%;
                padding: 13px;
                margin-bottom: 10px;
                border: 1px solid #ddd;
                border-radius: 10px;
                font-size: 16px;
            }

            #ogrenci-form {
                background: white;
                padding: 20px;
                margin-top: 15px;
                border-radius: 14px;
                display: none;
            }

        </style>

    </head>

    <body>

        <div class="container">

            <h1>DETAY SANAT AKADEMİ</h1>

            <div class="menu">

                <button onclick="ogrenciEkle()">
                    👤 Öğrenci Ekle
                </button>

                <a
                    href="/ogretmen"
                    class="button"
                >
                    🎨 Öğretmen Paneli
                </a>

                <a
                    href="/sonuclar"
                    class="button"
                >
                    📊 Öğrenci Sonuçları
                </a>

                <a
                    href="/"
                    class="button"
                >
                    🏠 Ana Menü
                </a>

                <a
                    href="/yonetici-cikis"
                    class="button danger"
                >
                    🚪 Çıkış
                </a>

            </div>

            <div id="ogrenci-form">

                <h3>Yeni Öğrenci</h3>

                <input
                    id="ogrenci-kodu"
                    placeholder="Öğrenci kodu"
                >

                <input
                    id="ogrenci-adi"
                    placeholder="Ad Soyad"
                >

                <button onclick="kaydetOgrenci()">
                    Kaydet
                </button>

            </div>

            <h2 style="margin-top:30px;">
                Öğrenciler
            </h2>

            <div id="ogrenciler">
                Yükleniyor...
            </div>

        </div>

        <script>

            function ogrenciEkle() {

                const form = document.getElementById(
                    "ogrenci-form"
                );

                form.style.display =
                    form.style.display === "block"
                        ? "none"
                        : "block";
            }


            async function kaydetOgrenci() {

                const kod =
                    document.getElementById(
                        "ogrenci-kodu"
                    ).value.trim();

                const ad =
                    document.getElementById(
                        "ogrenci-adi"
                    ).value.trim();

                if (!kod || !ad) {

                    alert(
                        "Öğrenci kodu ve ad soyad gerekli."
                    );

                    return;
                }

                const cevap = await fetch(
                    "/ogrenci-ekle",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify({
                            ogrenci_kodu: kod,
                            ad_soyad: ad
                        })
                    }
                );

                const veri =
                    await cevap.json();

                alert(veri.mesaj);

                if (veri.basarili) {

                    document.getElementById(
                        "ogrenci-kodu"
                    ).value = "";

                    document.getElementById(
                        "ogrenci-adi"
                    ).value = "";

                    document.getElementById(
                        "ogrenci-form"
                    ).style.display = "none";

                    ogrencileriYukle();
                }
            }


            async function ogrencileriYukle() {

                const cevap = await fetch(
                    "/ogrenciler"
                );

                const ogrenciler =
                    await cevap.json();

                const alan =
                    document.getElementById(
                        "ogrenciler"
                    );

                alan.innerHTML = "";

                if (!ogrenciler.length) {

                    alan.innerHTML =
                        "<p>Henüz öğrenci yok.</p>";

                    return;
                }

                ogrenciler.forEach(function(ogrenci) {

                    const div =
                        document.createElement("div");

                    div.className = "student";

                    div.innerHTML = `
                        <strong>
                            ${ogrenci.ad_soyad}
                        </strong>
                        <br>
                        Kod:
                        ${ogrenci.ogrenci_kodu}
                        <br>
                        <button
                            onclick="ogrenciSil(${ogrenci.id})"
                        >
                            Öğrenciyi Sil
                        </button>
                    `;

                    alan.appendChild(div);

                });
            }


            async function ogrenciSil(id) {

                const onay =
                    confirm(
                        "Bu öğrenciyi ve çalışmalarını silmek istediğinize emin misiniz?"
                    );

                if (!onay) {
                    return;
                }

                const cevap = await fetch(
                    "/ogrenci-sil/" + id,
                    {
                        method: "DELETE"
                    }
                );

                const veri =
                    await cevap.json();

                alert(veri.mesaj);

                if (veri.basarili) {
                    ogrencileriYukle();
                }
            }


            ogrencileriYukle();

        </script>

    </body>

    </html>
    """

    return html


# =========================================================
# ÖĞRETMEN PANELİ
# =========================================================

@app.route("/ogretmen")
@yonetici_gerekli
def ogretmen():

    return send_from_directory(
        BASE_DIR,
        "ogretmen.html"
    )


# =========================================================
# DEĞERLENDİRME SAYFASI
# =========================================================

@app.route("/degerlendir/<int:id>")
@yonetici_gerekli
def degerlendir(id):

    return send_from_directory(
        BASE_DIR,
        "degerlendir.html"
    )


# =========================================================
# YÜKLENEN DOSYALAR
# =========================================================

@app.route("/uploads/<filename>")
@yonetici_gerekli
def uploads(filename):

    return send_from_directory(
        UPLOAD_FOLDER,
        filename
    )


# =========================================================
# ÖĞRENCİ EKLE
# =========================================================

@app.route(
    "/ogrenci-ekle",
    methods=["POST"]
)
@yonetici_gerekli
def ogrenci_ekle_route():

    try:

        veri = request.get_json(
            silent=True
        ) or {}

        ogrenci_kodu = (
            veri.get("ogrenci_kodu", "")
            .strip()
            .upper()
        )

        ad_soyad = (
            veri.get("ad_soyad", "")
            .strip()
        )

        if not ogrenci_kodu or not ad_soyad:

            return jsonify({
                "basarili": False,
                "mesaj": "Öğrenci kodu ve ad soyad gerekli."
            }), 400

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
            "mesaj": str(e)
        }), 500


# =========================================================
# ÖĞRENCİLERİ GETİR
# =========================================================

@app.route("/ogrenciler")
@yonetici_gerekli
def ogrenciler():

    try:

        ogrenciler = ogrencileri_getir()

        liste = []

        for ogrenci in ogrenciler:

            liste.append({
                "id": ogrenci["id"],
                "ogrenci_kodu": ogrenci["ogrenci_kodu"],
                "ad_soyad": ogrenci["ad_soyad"]
            })

        return jsonify(liste)

    except Exception as e:

        return jsonify({
            "basarili": False,
            "mesaj": str(e)
        }), 500


# =========================================================
# ÖĞRENCİ SİL
# =========================================================

@app.route(
    "/ogrenci-sil/<int:id>",
    methods=["DELETE"]
)
@yonetici_gerekli
def ogrenci_sil(id):

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT *
            FROM ogrenciler
            WHERE id = ?
            """,
            (id,)
        )

        ogrenci = cursor.fetchone()

        if not ogrenci:

            conn.close()

            return jsonify({
                "basarili": False,
                "mesaj": "Öğrenci bulunamadı."
            }), 404

        cursor.execute(
            """
            SELECT fotograf
            FROM calismalar
            WHERE ogrenci_kodu = ?
            """,
            (ogrenci["ogrenci_kodu"],)
        )

        dosyalar = cursor.fetchall()

        cursor.execute(
            """
            DELETE FROM calismalar
            WHERE ogrenci_kodu = ?
            """,
            (ogrenci["ogrenci_kodu"],)
        )

        cursor.execute(
            """
            DELETE FROM ogrenciler
            WHERE id = ?
            """,
            (id,)
        )

        conn.commit()

        conn.close()

        for kayit in dosyalar:

            fotograf = kayit["fotograf"]

            if fotograf:

                dosya_yolu = os.path.join(
                    UPLOAD_FOLDER,
                    fotograf
                )

                if os.path.exists(dosya_yolu):

                    try:
                        os.remove(dosya_yolu)

                    except Exception:
                        pass

        return jsonify({
            "basarili": True,
            "mesaj": "Öğrenci ve çalışmaları silindi."
        })

    except Exception as e:

        conn.rollback()

        conn.close()

        return jsonify({
            "basarili": False,
            "mesaj": str(e)
        }), 500


# =========================================================
# ÇİZİM GÖNDER
# =========================================================

@app.route(
    "/gonder",
    methods=["GET", "POST"]
)
def gonder():

    # -----------------------------------------------------
    # GET = ÇİZİM GÖNDERME SAYFASI
    # -----------------------------------------------------

    if request.method == "GET":

        return """
        <!DOCTYPE html>
        <html lang="tr">

        <head>

            <meta charset="UTF-8">

            <meta
                name="viewport"
                content="width=device-width, initial-scale=1.0"
            >

            <title>Çizim Gönder - Detay Sanat Akademi</title>

            <style>

                * {
                    box-sizing: border-box;
                }

                body {
                    margin: 0;
                    background: #f4f4f4;
                    font-family: Arial, sans-serif;
                    color: #222;
                }

                /* -----------------------------------------
                   ANA KONTEYNER
                ----------------------------------------- */

                .container {
                    width: 92%;
                    max-width: 500px;
                    margin: 0 auto;
                    padding: 25px 0 35px;
                }

                /* -----------------------------------------
                   ÜST LOGO ALANI
                ----------------------------------------- */

                .ust {
                    text-align: center;
                    margin-bottom: 10px;
                }

                .ust img {
                    width: 130px;
                    max-width: 50%;
                    height: auto;
                    display: block;
                    margin: 0 auto 12px;
                }

                .ust h1 {
                    margin: 0;
                    font-size: 23px;
                    letter-spacing: 1px;
                }

                .alt-baslik {
                    margin-top: 7px;
                    color: #666;
                    font-size: 14px;
                }

                /* -----------------------------------------
                   ANA MENÜ BUTONU
                ----------------------------------------- */

                .ana-menu-alan {
                    text-align: center;
                    margin: 18px 0 20px;
                }

                .ana-menu {
                    display: inline-block;

                    padding: 10px 20px;

                    background: #222;
                    color: white;

                    text-decoration: none;

                    border-radius: 25px;

                    font-size: 14px;
                    font-weight: bold;

                    box-shadow:
                        0 3px 10px
                        rgba(0,0,0,0.15);

                    transition: 0.2s;
                }

                .ana-menu:hover {
                    transform: translateY(-1px);
                    opacity: 0.9;
                }

                /* -----------------------------------------
                   FORM KARTI
                ----------------------------------------- */

                .card {
                    background: white;

                    padding: 25px;

                    border-radius: 18px;

                    box-shadow:
                        0 4px 15px
                        rgba(0,0,0,0.08);
                }

                .card h2 {
                    text-align: center;
                    margin-top: 0;
                    margin-bottom: 20px;
                    font-size: 20px;
                }

                label {
                    display: block;

                    margin-top: 18px;
                    margin-bottom: 7px;

                    font-weight: bold;
                }

                input,
                select {
                    width: 100%;

                    padding: 14px;

                    border:
                        1px solid #ddd;

                    border-radius: 10px;

                    font-size: 16px;

                    background: white;
                }

                input:focus,
                select:focus {
                    outline: none;

                    border-color: #222;
                }

                button {
                    width: 100%;

                    margin-top: 22px;

                    padding: 15px;

                    border: none;

                    border-radius: 10px;

                    background: #222;
                    color: white;

                    font-size: 16px;
                    font-weight: bold;

                    cursor: pointer;
                }

                button:hover {
                    opacity: 0.9;
                }

                #sonuc {
                    margin-top: 20px;

                    text-align: center;

                    font-weight: bold;

                    line-height: 1.5;
                }

                /* -----------------------------------------
                   TELEFON
                ----------------------------------------- */

                @media (max-width: 600px) {

                    .container {
                        width: 94%;
                        padding-top: 20px;
                    }

                    .ust img {
                        width: 115px;
                    }

                    .ust h1 {
                        font-size: 20px;
                    }

                    .alt-baslik {
                        font-size: 13px;
                    }

                    .ana-menu-alan {
                        margin-top: 15px;
                        margin-bottom: 18px;
                    }

                    .ana-menu {
                        padding: 9px 18px;
                        font-size: 13px;
                    }

                    .card {
                        padding: 20px;
                        border-radius: 16px;
                    }

                    input,
                    select {
                        padding: 13px;
                    }

                    button {
                        padding: 14px;
                    }

                }

            </style>

        </head>

        <body>

            <div class="container">

                <!-- LOGO VE BAŞLIK -->

                <div class="ust">

                    <img
                        src="/static/logo.png"
                        alt="Detay Sanat Akademi"
                    >

                    <h1>
                        DETAY SANAT AKADEMİ
                    </h1>

                    <div class="alt-baslik">
                        Çizim Gönder
                    </div>

                </div>


                <!-- ANA MENÜ -->

                <div class="ana-menu-alan">

                    <a
                        href="/"
                        class="ana-menu"
                    >
                        ← ANA MENÜ
                    </a>

                </div>


                <!-- FORM -->

                <div class="card">

                    <h2>
                        🎨 Çizim Gönder
                    </h2>

                    <form
                        id="gonderForm"
                        enctype="multipart/form-data"
                    >

                        <label>
                            Öğrenci Kodu
                        </label>

                        <input
                            type="text"
                            name="ogrenci_kodu"
                            placeholder="Örn: DS002"
                            required
                        >


                        <label>
                            Çalışma Türü
                        </label>

                        <select
                            name="calisma_turu"
                            required
                        >

                            <option value="">
                                Seçiniz
                            </option>

                            <option value="GSF Hazırlık">
                                GSF Hazırlık
                            </option>

                            <option value="Çocuk Resim">
                                Çocuk Resim
                            </option>

                        </select>


                        <label>
                            Çizim Fotoğrafı
                        </label>

                        <input
                            type="file"
                            name="fotograf"
                            accept="image/*"
                            capture="environment"
                            required
                        >


                        <button type="submit">
                            Çizimi Gönder
                        </button>

                    </form>


                    <div id="sonuc"></div>

                </div>

            </div>


            <script>

                document
                    .getElementById("gonderForm")
                    .addEventListener(
                        "submit",
                        async function(event) {

                            event.preventDefault();

                            const sonuc =
                                document.getElementById(
                                    "sonuc"
                                );

                            const formData =
                                new FormData(this);

                            sonuc.textContent =
                                "Gönderiliyor...";

                            try {

                                const cevap =
                                    await fetch(
                                        "/gonder",
                                        {
                                            method: "POST",
                                            body: formData
                                        }
                                    );

                                const veri =
                                    await cevap.json();

                                sonuc.textContent =
                                    veri.mesaj;

                                if (veri.basarili) {

                                    this.reset();

                                }

                            } catch (hata) {

                                sonuc.textContent =
                                    "Gönderme sırasında bir hata oluştu.";

                                console.error(hata);

                            }

                        }
                    );

            </script>

        </body>

        </html>
        """

    # -----------------------------------------------------
    # POST = ÇİZİMİ KAYDET
    # -----------------------------------------------------

    try:

    try:

        ogrenci_kodu = (
            request.form
            .get("ogrenci_kodu", "")
            .strip()
            .upper()
        )

        calisma_turu = (
            request.form
            .get("calisma_turu", "")
            .strip()
        )

        fotograf = request.files.get(
            "fotograf"
        )

        if not ogrenci_kodu:

            return jsonify({
                "basarili": False,
                "mesaj": "Öğrenci kodu gerekli."
            }), 400

        if not calisma_turu:

            return jsonify({
                "basarili": False,
                "mesaj": "Çalışma türü seçiniz."
            }), 400

        if not fotograf:

            return jsonify({
                "basarili": False,
                "mesaj": "Lütfen çizim fotoğrafı seçiniz."
            }), 400

        if not fotograf.filename:

            return jsonify({
                "basarili": False,
                "mesaj": "Dosya seçilmedi."
            }), 400

        # Öğrenciyi bul

        conn = sqlite3.connect(DATABASE)

        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT ogrenci_kodu, ad_soyad
            FROM ogrenciler
            WHERE ogrenci_kodu = ?
            """,
            (ogrenci_kodu,)
        )

        ogrenci = cursor.fetchone()

        conn.close()

        if not ogrenci:

            return jsonify({
                "basarili": False,
                "mesaj": "Bu öğrenci kodu bulunamadı."
            }), 404

        ogrenci_adi = ogrenci["ad_soyad"]

        # Dosya adını güvenli hale getir

        dosya_adi = secure_filename(
            fotograf.filename
        )

        if not dosya_adi:

            dosya_adi = "cizim.jpg"

        zaman = int(
            time.time()
        )

        yeni_dosya_adi = (
            f"{zaman}_{dosya_adi}"
        )

        dosya_yolu = os.path.join(
            UPLOAD_FOLDER,
            yeni_dosya_adi
        )

        fotograf.save(
            dosya_yolu
        )

        # Veritabanına kaydet

        calisma_id = calisma_ekle(
            ogrenci_adi,
            calisma_turu,
            yeni_dosya_adi,
            ogrenci_kodu
        )

        return jsonify({
            "basarili": True,
            "mesaj": "Çizimin başarıyla gönderildi.",
            "id": calisma_id
        })

    except Exception as e:

        return jsonify({
            "basarili": False,
            "mesaj": f"Çizim gönderilirken hata oluştu: {str(e)}"
        }), 500


# =========================================================
# TÜM ÇALIŞMALAR
# =========================================================

@app.route("/calismalar")
@yonetici_gerekli
def calismalar():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM calismalar
        ORDER BY id DESC
        """
    )

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


# =========================================================
# ÖĞRENCİ SONUÇLARI
# =========================================================

@app.route(
    "/ogrenci-sonuclari/<ogrenci_kodu>"
)
def ogrenci_sonuclari(ogrenci_kodu):

    ogrenci_kodu = (
        ogrenci_kodu
        .strip()
        .upper()
    )

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    # Öğrenciyi getir

    cursor.execute(
        """
        SELECT *
        FROM ogrenciler
        WHERE ogrenci_kodu = ?
        """,
        (ogrenci_kodu,)
    )

    ogrenci = cursor.fetchone()

    if not ogrenci:

        conn.close()

        return jsonify({
            "basarili": False,
            "mesaj": "Öğrenci bulunamadı."
        }), 404

    # Çalışmaları getir

    cursor.execute(
        """
        SELECT *
        FROM calismalar
        WHERE ogrenci_kodu = ?
        ORDER BY id DESC
        """,
        (ogrenci_kodu,)
    )

    calisma_kayitlari = cursor.fetchall()

    conn.close()

    calismalar_listesi = []

    for kayit in calisma_kayitlari:

        puanlar = {
            "kompozisyon": kayit["kompozisyon"],
            "oran_oranti": kayit["oran_oranti"],
            "perspektif": kayit["perspektif"],
            "isik_golge": kayit["isik_golge"],
            "cizgi_kullanimi": kayit["cizgi_kullanimi"]
        }

        toplam = None

        puan_degerleri = [
            kayit["kompozisyon"],
            kayit["oran_oranti"],
            kayit["perspektif"],
            kayit["isik_golge"],
            kayit["cizgi_kullanimi"]
        ]

        if all(
            puan is not None
            for puan in puan_degerleri
        ):

            toplam = sum(
                puan_degerleri
            )

        calismalar_listesi.append({

            "id": kayit["id"],

            "calisma_turu":
                kayit["calisma_turu"],

            "fotograf":
                kayit["fotograf"],

            "durum":
                kayit["durum"],

            "tarih":
                kayit["tarih"],

            "puanlar":
                puanlar,

            "toplam":
                toplam,

            "yorum":
                kayit["yorum"]

        })

    return jsonify({

        "basarili": True,

        "ogrenci": {
            "id": ogrenci["id"],
            "ogrenci_kodu":
                ogrenci["ogrenci_kodu"],
            "ad_soyad":
                ogrenci["ad_soyad"]
        },

        "calismalar":
            calismalar_listesi

    })


# =========================================================
# TEK ÇALIŞMA
# =========================================================

@app.route(
    "/calisma/<int:id>"
)
@yonetici_gerekli
def calisma(id):

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM calismalar
        WHERE id = ?
        """,
        (id,)
    )

    kayit = cursor.fetchone()

    conn.close()

    if not kayit:

        return jsonify({
            "basarili": False,
            "mesaj": "Çalışma bulunamadı."
        }), 404

    return jsonify({

        "basarili": True,

        "calisma": {
            "id":
                kayit["id"],

            "ogrenci_adi":
                kayit["ogrenci_adi"],

            "ogrenci_kodu":
                kayit["ogrenci_kodu"],

            "calisma_turu":
                kayit["calisma_turu"],

            "fotograf":
                kayit["fotograf"],

            "durum":
                kayit["durum"],

            "tarih":
                kayit["tarih"],

            "kompozisyon":
                kayit["kompozisyon"],

            "oran_oranti":
                kayit["oran_oranti"],

            "perspektif":
                kayit["perspektif"],

            "isik_golge":
                kayit["isik_golge"],

            "cizgi_kullanimi":
                kayit["cizgi_kullanimi"],

            "yorum":
                kayit["yorum"]
        }

    })


# =========================================================
# DEĞERLENDİRME KAYDET
# =========================================================

@app.route(
    "/degerlendirme-kaydet",
    methods=["POST"]
)
@yonetici_gerekli
def degerlendirme_kaydet():

    try:

        veri = request.get_json(
            silent=True
        ) or {}

        calisma_id = veri.get("id")

        if calisma_id is None:

            return jsonify({
                "basarili": False,
                "mesaj": "Çalışma ID gerekli."
            }), 400

        try:

            calisma_id = int(
                calisma_id
            )

        except ValueError:

            return jsonify({
                "basarili": False,
                "mesaj": "Geçersiz çalışma ID."
            }), 400

        kriterler = [
            "kompozisyon",
            "oran_oranti",
            "perspektif",
            "isik_golge",
            "cizgi_kullanimi"
        ]

        puanlar = {}

        izin_verilen_puanlar = {
            5,
            10,
            15,
            20
        }

        for kriter in kriterler:

            deger = veri.get(
                kriter
            )

            if deger is None:

                return jsonify({
                    "basarili": False,
                    "mesaj":
                        f"{kriter} puanı gerekli."
                }), 400

            try:

                deger = int(deger)

            except (TypeError, ValueError):

                return jsonify({
                    "basarili": False,
                    "mesaj":
                        f"{kriter} puanı geçersiz."
                }), 400

            if deger not in izin_verilen_puanlar:

                return jsonify({
                    "basarili": False,
                    "mesaj":
                        "Puanlar 5, 10, 15 veya 20 olmalıdır."
                }), 400

            puanlar[kriter] = deger

        yorum = (
            veri.get("yorum", "")
            .strip()
        )

        toplam = sum(
            puanlar.values()
        )

        conn = sqlite3.connect(DATABASE)

        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM calismalar
            WHERE id = ?
            """,
            (calisma_id,)
        )

        kayit = cursor.fetchone()

        if not kayit:

            conn.close()

            return jsonify({
                "basarili": False,
                "mesaj": "Çalışma bulunamadı."
            }), 404

        cursor.execute(
            """
            UPDATE calismalar

            SET
                kompozisyon = ?,
                oran_oranti = ?,
                perspektif = ?,
                isik_golge = ?,
                cizgi_kullanimi = ?,
                yorum = ?,
                durum = 'Değerlendirildi'

            WHERE id = ?
            """,
            (
                puanlar["kompozisyon"],
                puanlar["oran_oranti"],
                puanlar["perspektif"],
                puanlar["isik_golge"],
                puanlar["cizgi_kullanimi"],
                yorum,
                calisma_id
            )
        )

        conn.commit()

        # Güncellenmiş kaydı tekrar al

        cursor.execute(
            """
            SELECT fotograf
            FROM calismalar
            WHERE id = ?
            """,
            (calisma_id,)
        )

        guncel_kayit = cursor.fetchone()

        conn.close()

        # Değerlendirilmiş fotoğrafı sil

        if guncel_kayit:

            fotograf = guncel_kayit["fotograf"]

            if fotograf:

                dosya_yolu = os.path.join(
                    UPLOAD_FOLDER,
                    fotograf
                )

                if os.path.exists(dosya_yolu):

                    try:

                        os.remove(
                            dosya_yolu
                        )

                    except Exception:

                        pass

        return jsonify({

            "basarili": True,

            "mesaj":
                "Değerlendirme başarıyla kaydedildi.",

            "toplam":
                toplam

        })

    except Exception as e:

        return jsonify({

            "basarili": False,

            "mesaj":
                f"Değerlendirme kaydedilirken hata oluştu: {str(e)}"

        }), 500


# =========================================================
# SUNUCU
# =========================================================

if __name__ == "__main__":

    print()
    print(
        "DETAY SANAT AKADEMİ sunucusu başlıyor..."
    )

    print(
        "Bilgisayardan: http://127.0.0.1:5000"
    )

    print(
        "Telefondan: http://192.168.0.18:5000"
    )

    print(
        "Yönetici: http://127.0.0.1:5000/yonetici-giris"
    )

    print()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )