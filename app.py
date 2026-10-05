```python
from flask import (
    Flask,
    request,
    jsonify,
    send_from_directory,
    render_template,
    session,
    redirect,
    url_for
)

import os
import sqlite3
import secrets
from functools import wraps
from werkzeug.utils import secure_filename

from database import (
    veritabani_olustur,
    calisma_ekle,
    ogrenci_ekle,
    ogrencileri_getir
)


# ==================================================
# UYGULAMA
# ==================================================

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "local-development-secret-key"
)

ADMIN_PASSWORD = os.environ.get(
    "ADMIN_PASSWORD",
    ""
)

UPLOAD_FOLDER = "uploads"
DATABASE = "detay_sanat.db"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

veritabani_olustur()


# ==================================================
# YÖNETİCİ GÜVENLİK
# ==================================================

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


# ==================================================
# ANA SAYFA
# ==================================================

@app.route("/")
def home():

    return send_from_directory(
        ".",
        "index.html"
    )


# ==================================================
# ÖĞRENCİ BÖLÜMLERİ
# ==================================================

@app.route("/ogrenci-giris")
def ogrenci_giris():

    return render_template(
        "ogrenci_giris.html"
    )


@app.route("/ogrenci-panel")
def ogrenci_panel():

    return render_template(
        "ogrenci_panel.html"
    )


@app.route("/sonuclar")
def sonuclar():

    return send_from_directory(
        ".",
        "sonuclar.html"
    )


# ==================================================
# YÖNETİCİ GİRİŞ
# ==================================================

@app.route(
    "/yonetici-giris",
    methods=["GET", "POST"]
)
def yonetici_giris():

    if request.method == "GET":

        if session.get("yonetici_giris"):

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

            <title>Yönetici Girişi</title>

            <style>

                body {
                    margin: 0;
                    font-family: Arial, sans-serif;
                    background: #f3f0f7;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                }

                .kutu {
                    width: 90%;
                    max-width: 400px;
                    background: white;
                    padding: 30px;
                    border-radius: 20px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.12);
                    box-sizing: border-box;
                }

                h1 {
                    text-align: center;
                    margin-bottom: 25px;
                    color: #333;
                }

                input {
                    width: 100%;
                    padding: 14px;
                    margin-bottom: 15px;
                    border: 1px solid #ddd;
                    border-radius: 10px;
                    box-sizing: border-box;
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

                button:hover {
                    background: #444;
                }

            </style>

        </head>

        <body>

            <div class="kutu">

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

            </div>

        </body>

        </html>
        """

    sifre = request.form.get(
        "sifre",
        ""
    )

    if not ADMIN_PASSWORD:

        return """
        <h2>Yönetici şifresi ayarlanmamış.</h2>
        <p>ADMIN_PASSWORD tanımlayın.</p>
        """

    if secrets.compare_digest(
        sifre,
        ADMIN_PASSWORD
    ):

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

        <title>Yönetici Girişi</title>

    </head>

    <body
        style="
            font-family: Arial;
            text-align: center;
            padding: 50px;
        "
    >

        <h2>❌ Şifre yanlış</h2>

        <p>
            <a href="/yonetici-giris">
                Tekrar dene
            </a>
        </p>

    </body>

    </html>
    """, 401


# ==================================================
# YÖNETİCİ ÇIKIŞ
# ==================================================

@app.route("/yonetici-cikis")
def yonetici_cikis():

    session.clear()

    return redirect(
        url_for("home")
    )


# ==================================================
# YÖNETİCİ PANELİ
# ==================================================

@app.route("/yonetici-panel")
@yonetici_gerekli
def yonetici_panel():

    return """
    <!DOCTYPE html>
    <html lang="tr">

    <head>

        <meta charset="UTF-8">

        <meta
            name="viewport"
            content="width=device-width, initial-scale=1.0"
        >

        <title>Detay Sanat Akademi - Yönetici Paneli</title>

        <style>

            * {
                box-sizing: border-box;
            }

            body {
                margin: 0;
                font-family: Arial, sans-serif;
                background: #f5f3f7;
                color: #222;
            }

            header {
                background: #222;
                color: white;
                padding: 20px;
                text-align: center;
            }

            header h1 {
                margin: 0;
            }

            .container {
                width: 94%;
                max-width: 1100px;
                margin: 30px auto;
            }

            .kartlar {
                display: grid;
                grid-template-columns:
                    repeat(auto-fit, minmax(220px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }

            .kart {
                background: white;
                padding: 25px;
                border-radius: 18px;
                box-shadow:
                    0 5px 20px rgba(0,0,0,0.08);
            }

            .kart h2 {
                margin-top: 0;
            }

            .buton {
                display: block;
                width: 100%;
                padding: 14px;
                margin-top: 10px;
                border: none;
                border-radius: 10px;
                background: #222;
                color: white;
                cursor: pointer;
                text-decoration: none;
                text-align: center;
                font-size: 15px;
            }

            .buton:hover {
                background: #444;
            }

            .cikis {
                background: #a40000;
            }

            .cikis:hover {
                background: #c00000;
            }

            #ogrenciListesi {
                margin-top: 20px;
            }

            .ogrenci {
                background: white;
                padding: 18px;
                border-radius: 12px;
                margin-bottom: 10px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 15px;
            }

            .ogrenci-bilgi {
                flex: 1;
            }

            .sil {
                background: #b00020;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 15px;
                cursor: pointer;
            }

            @media (max-width: 600px) {

                .ogrenci {
                    flex-direction: column;
                    align-items: stretch;
                }

            }

        </style>

    </head>

    <body>

        <header>

            <h1>
                DETAY SANAT AKADEMİ
            </h1>

            <p>
                Yönetici Paneli
            </p>

        </header>


        <div class="container">

            <div class="kartlar">

                <div class="kart">

                    <h2>👨‍🎓 Öğrenci Kayıt</h2>

                    <p>
                        Yeni öğrenci ekleyebilirsiniz.
                    </p>

                    <button
                        class="buton"
                        onclick="ogrenciEkle()"
                    >
                        Öğrenci Ekle
                    </button>

                </div>


                <div class="kart">

                    <h2>📝 Değerlendirme</h2>

                    <p>
                        Gelen çizimleri görüntüleyin
                        ve değerlendirin.
                    </p>

                    <a
                        class="buton"
                        href="/ogretmen"
                    >
                        Gelen Çizimler
                    </a>

                </div>


                <div class="kart">

                    <h2>📊 Sonuçlar</h2>

                    <p>
                        Öğrenci sonuçlarını kontrol edin.
                    </p>

                    <a
                        class="buton"
                        href="/sonuclar"
                    >
                        Sonuçlar
                    </a>

                </div>


                <div class="kart">

                    <h2>🔐 Hesap</h2>

                    <p>
                        Yönetici oturumunu kapatın.
                    </p>

                    <a
                        class="buton cikis"
                        href="/yonetici-cikis"
                    >
                        Çıkış Yap
                    </a>

                </div>

            </div>


            <div class="kart">

                <h2>👨‍🎓 Kayıtlı Öğrenciler</h2>

                <div id="ogrenciListesi">
                    Öğrenciler yükleniyor...
                </div>

            </div>

        </div>


        <script>

            async function ogrencileriYukle() {

                try {

                    const cevap =
                        await fetch("/ogrenciler");

                    if (!cevap.ok) {

                        document.getElementById(
                            "ogrenciListesi"
                        ).innerHTML =
                            "Öğrenciler yüklenemedi.";

                        return;
                    }

                    const ogrenciler =
                        await cevap.json();

                    const liste =
                        document.getElementById(
                            "ogrenciListesi"
                        );

                    if (ogrenciler.length === 0) {

                        liste.innerHTML =
                            "<p>Henüz öğrenci yok.</p>";

                        return;
                    }

                    liste.innerHTML = "";

                    ogrenciler.forEach(
                        function(ogrenci) {

                            const div =
                                document.createElement(
                                    "div"
                                );

                            div.className = "ogrenci";

                            div.innerHTML = `
                                <div class="ogrenci-bilgi">

                                    <strong>
                                        ${ogrenci.ad_soyad}
                                    </strong>

                                    <br>

                                    <small>
                                        Kod:
                                        ${ogrenci.ogrenci_kodu}
                                    </small>

                                </div>

                                <button
                                    class="sil"
                                    onclick="ogrenciSil(
                                        ${ogrenci.id},
                                        '${ogrenci.ad_soyad.replace(
                                            /'/g,
                                            "\\'"
                                        )}'
                                    )"
                                >
                                    Öğrenciyi Sil
                                </button>
                            `;

                            liste.appendChild(div);

                        }
                    );

                } catch (hata) {

                    document.getElementById(
                        "ogrenciListesi"
                    ).innerHTML =
                        "Sunucu bağlantısı kurulamadı.";

                }

            }


            async function ogrenciEkle() {

                const adSoyad =
                    prompt(
                        "Öğrencinin ad soyadını girin:"
                    );

                if (!adSoyad) {
                    return;
                }

                const ogrenciKodu =
                    prompt(
                        "Öğrenci kodunu girin:"
                    );

                if (!ogrenciKodu) {
                    return;
                }

                try {

                    const cevap =
                        await fetch(
                            "/ogrenci-ekle",
                            {
                                method: "POST",

                                headers: {
                                    "Content-Type":
                                        "application/json"
                                },

                                body: JSON.stringify({
                                    ad_soyad:
                                        adSoyad,

                                    ogrenci_kodu:
                                        ogrenciKodu
                                })
                            }
                        );

                    const sonuc =
                        await cevap.json();

                    alert(sonuc.mesaj);

                    if (sonuc.basarili) {
                        ogrencileriYukle();
                    }

                } catch (hata) {

                    alert(
                        "Sunucu bağlantısı kurulamadı."
                    );

                }

            }


            async function ogrenciSil(
                id,
                adSoyad
            ) {

                const onay =
                    confirm(
                        adSoyad +
                        " isimli öğrenciyi silmek istediğinize emin misiniz?\n\n" +
                        "Bu işlem öğrencinin kayıtlarını ve değerlendirme geçmişini de silecektir."
                    );

                if (!onay) {
                    return;
                }

                try {

                    const cevap =
                        await fetch(
                            "/ogrenci-sil/" + id,
                            {
                                method: "DELETE"
                            }
                        );

                    const sonuc =
                        await cevap.json();

                    alert(sonuc.mesaj);

                    if (sonuc.basarili) {
                        ogrencileriYukle();
                    }

                } catch (hata) {

                    alert(
                        "Silme işlemi sırasında hata oluştu."
                    );

                }

            }


            ogrencileriYukle();

        </script>

    </body>

    </html>
    """


# ==================================================
# ÖĞRETMEN PANELİ
# ==================================================

@app.route("/ogretmen")
@yonetici_gerekli
def ogretmen():

    return send_from_directory(
        ".",
        "ogretmen.html"
    )


# ==================================================
# DEĞERLENDİRME SAYFASI
# ==================================================

@app.route("/degerlendir/<int:id>")
@yonetici_gerekli
def degerlendir(id):

    return send_from_directory(
        ".",
        "degerlendir.html"
    )


# ==================================================
# UPLOADS
# ==================================================

@app.route("/uploads/<filename>")
@yonetici_gerekli
def uploads(filename):

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )


# ==================================================
# ÖĞRENCİ EKLE
# ==================================================

@app.route(
    "/ogrenci-ekle",
    methods=["POST"]
)
@yonetici_gerekli
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
            "mesaj":
                f"Öğrenci eklenemedi: {str(e)}"
        })


# ==================================================
# ÖĞRENCİLERİ GETİR
# ==================================================

@app.route("/ogrenciler")
@yonetici_gerekli
def ogrenciler():

    kayitlar = ogrencileri_getir()

    liste = []

    for kayit in kayitlar:

        liste.append({
            "id": kayit["id"],
            "ogrenci_kodu":
                kayit["ogrenci_kodu"],
            "ad_soyad":
                kayit["ad_soyad"]
        })

    return jsonify(liste)


# ==================================================
# ÖĞRENCİ SİL
# ==================================================

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

        cursor.execute("""
            SELECT
                id,
                ogrenci_kodu,
                ad_soyad
            FROM ogrenciler
            WHERE id = ?
        """, (id,))

        ogrenci = cursor.fetchone()

        if not ogrenci:

            conn.close()

            return jsonify({
                "basarili": False,
                "mesaj":
                    "Öğrenci bulunamadı."
            }), 404

        ogrenci_kodu =
            ogrenci["ogrenci_kodu"]

        cursor.execute("""
            SELECT
                fotograf
            FROM calismalar
            WHERE ogrenci_kodu = ?
        """, (ogrenci_kodu,))

        calismalar = cursor.fetchall()

        silinecek_dosyalar = []

        for calisma in calismalar:

            fotograf = calisma["fotograf"]

            if fotograf:

                silinecek_dosyalar.append(
                    fotograf
                )

        cursor.execute("""
            DELETE FROM calismalar
            WHERE ogrenci_kodu = ?
        """, (ogrenci_kodu,))

        cursor.execute("""
            DELETE FROM ogrenciler
            WHERE id = ?
        """, (id,))

        conn.commit()

        conn.close()

        for fotograf in silinecek_dosyalar:

            dosya_yolu = os.path.join(
                app.config["UPLOAD_FOLDER"],
                fotograf
            )

            if os.path.exists(dosya_yolu):

                try:

                    os.remove(dosya_yolu)

                except Exception as e:

                    print(
                        "Dosya silinemedi:",
                        fotograf,
                        str(e)
                    )

        return jsonify({
            "basarili": True,
            "mesaj":
                "Öğrenci ve tüm kayıtları başarıyla silindi."
        })

    except Exception as e:

        conn.rollback()

        conn.close()

        return jsonify({
            "basarili": False,
            "mesaj":
                f"Öğrenci silinemedi: {str(e)}"
        }), 500


# ==================================================
# ÇALIŞMA GÖNDER
# GET  = SAYFAYI AÇAR
# POST = ÇALIŞMAYI KAYDEDER
# ==================================================

@app.route(
    "/gonder",
    methods=["GET", "POST"]
)
def gonder():

    # --------------------------------------------------
    # GET
    # --------------------------------------------------

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

            <title>
                Çizim Gönder - Detay Sanat Akademi
            </title>

            <style>

                * {
                    box-sizing: border-box;
                }

                body {

                    margin: 0;

                    font-family:
                        Arial,
                        sans-serif;

                    background: #f4f4f4;

                    color: #222;
                }

                .container {

                    width: 92%;

                    max-width: 500px;

                    margin: 0 auto;

                    padding:
                        25px 0 40px;
                }

                .ust {

                    display: flex;

                    align-items: center;

                    gap: 12px;

                    margin-bottom: 25px;

                    flex-wrap: wrap;
                }

                .ana-menu {

                    display: inline-block;

                    padding:
                        11px 16px;

                    background: #222;

                    color: white;

                    text-decoration: none;

                    border-radius: 10px;

                    font-size: 14px;
                }

                .ana-menu:hover {

                    background: #444;
                }

                h1 {

                    margin: 0;

                    font-size: 25px;
                }

                .kart {

                    background: white;

                    padding: 25px;

                    border-radius: 18px;

                    box-shadow:
                        0 5px 20px
                        rgba(0,0,0,0.08);
                }

                label {

                    display: block;

                    margin-bottom: 8px;

                    font-weight: bold;
                }

                input,
                select {

                    width: 100%;

                    padding: 14px;

                    margin-bottom: 18px;

                    border:
                        1px solid #ddd;

                    border-radius: 10px;

                    font-size: 16px;
                }

                button {

                    width: 100%;

                    padding: 15px;

                    border: none;

                    border-radius: 10px;

                    background: #222;

                    color: white;

                    font-size: 16px;

                    cursor: pointer;
                }

                button:hover {

                    background: #444;
                }

                #mesaj {

                    margin-top: 18px;

                    text-align: center;

                    font-weight: bold;
                }

            </style>

        </head>

        <body>

            <div class="container">

                <div class="ust">

                    <a
                        href="/"
                        class="ana-menu"
                    >
                        ← Ana Menü
                    </a>

                    <h1>
                        🎨 Çizim Gönder
                    </h1>

                </div>


                <div class="kart">

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
                            placeholder="Örn: DS001"
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

                            <option
                                value="Güzel Sanatlar Fakültelerine Hazırlık"
                            >
                                GSF Hazırlık
                            </option>

                            <option
                                value="Çocuk Resim Kursu"
                            >
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


                        <button
                            type="submit"
                        >
                            Çizimi Gönder
                        </button>

                    </form>


                    <div id="mesaj"></div>

                </div>

            </div>


            <script>

                document
                    .getElementById(
                        "gonderForm"
                    )
                    .addEventListener(
                        "submit",
                        async function(event) {

                            event.preventDefault();

                            const form =
                                document.getElementById(
                                    "gonderForm"
                                );

                            const mesaj =
                                document.getElementById(
                                    "mesaj"
                                );

                            const veri =
                                new FormData(
                                    form
                                );

                            mesaj.innerHTML =
                                "Gönderiliyor...";

                            try {

                                const cevap =
                                    await fetch(
                                        "/gonder",
                                        {
                                            method:
                                                "POST",
                                            body:
                                                veri
                                        }
                                    );

                                const sonuc =
                                    await cevap.json();

                                if (
                                    sonuc.basarili
                                ) {

                                    mesaj.innerHTML =
                                        "✅ " +
                                        sonuc.mesaj;

                                    form.reset();

                                } else {

                                    mesaj.innerHTML =
                                        "❌ " +
                                        sonuc.mesaj;

                                }

                            } catch (hata) {

                                mesaj.innerHTML =
                                    "❌ Sunucu bağlantısı kurulamadı.";

                            }

                        }
                    );

            </script>

        </body>

        </html>
        """


    # --------------------------------------------------
    # POST
    # --------------------------------------------------

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
            "mesaj":
                "Öğrenci kodu girilmedi."
        })

    if not fotograf:

        return jsonify({
            "basarili": False,
            "mesaj":
                "Çizim fotoğrafı gönderilmedi."
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
            "mesaj":
                "Bu öğrenci kodu kayıtlı değil."
        })

    ogrenci_adi =
        ogrenci["ad_soyad"]

    dosya_adi =
        secure_filename(
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

    fotograf.save(
        dosya_yolu
    )

    calisma_id = calisma_ekle(
        ogrenci_adi,
        calisma_turu,
        yeni_dosya_adi,
        ogrenci_kodu
    )

    print()
    print(
        "Yeni öğrenci çalışması geldi!"
    )
    print(
        "-----------------------------"
    )
    print(
        "ID:",
        calisma_id
    )
    print(
        "Öğrenci kodu:",
        ogrenci_kodu
    )
    print(
        "Öğrenci:",
        ogrenci_adi
    )
    print(
        "Çalışma:",
        calisma_turu
    )
    print(
        "Fotoğraf:",
        yeni_dosya_adi
    )
    print(
        "-----------------------------"
    )
    print()

    return jsonify({
        "basarili": True,
        "mesaj":
            "Çizimin başarıyla gönderildi.",
        "id":
            calisma_id
    })


# ==================================================
# ÇALIŞMALAR
# ==================================================

@app.route("/calismalar")
@yonetici_gerekli
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
                kayit["tarih"]

        })

    return jsonify(liste)


# ==================================================
# ÖĞRENCİ SONUÇLARI API
# ==================================================

@app.route(
    "/ogrenci-sonuclari/<ogrenci_kodu>"
)
def ogrenci_sonuclari(ogrenci_kodu):

    ogrenci_kodu = (
        ogrenci_kodu
        .strip()
        .upper()
    )

    conn = sqlite3.connect(
        DATABASE
    )

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
            "mesaj":
                "Öğrenci bulunamadı."
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

    calisma_kayitlari =
        cursor.fetchall()

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

            "id":
                calisma["id"],

            "calisma_turu":
                calisma["calisma_turu"],

            "durum":
                calisma["durum"],

            "kompozisyon":
                calisma["kompozisyon"],

            "oran_oranti":
                calisma["oran_oranti"],

            "perspektif":
                calisma["perspektif"],

            "isik_golge":
                calisma["isik_golge"],

            "cizgi_kullanimi":
                calisma["cizgi_kullanimi"],

            "toplam":
                toplam,

            "yorum":
                calisma["yorum"],

            "tarih":
                calisma["tarih"]

        })

    return jsonify({

        "basarili":
            True,

        "ogrenci": {

            "ogrenci_kodu":
                ogrenci["ogrenci_kodu"],

            "ad_soyad":
                ogrenci["ad_soyad"]

        },

        "calismalar":
            liste

    })


# ==================================================
# TEK ÇALIŞMA
# ==================================================

@app.route("/calisma/<int:id>")
@yonetici_gerekli
def calisma(id):

    conn = sqlite3.connect(
        DATABASE
    )

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
            "mesaj":
                "Çalışma bulunamadı."
        }), 404

    return jsonify({

        "id":
            kayit["id"],

        "ogrenci_adi":
            kayit["ogrenci_adi"],

        "calisma_turu":
            kayit["calisma_turu"],

        "fotograf":
            kayit["fotograf"],

        "durum":
            kayit["durum"]

    })


# ==================================================
# DEĞERLENDİRME KAYDET
# ==================================================

@app.route(
    "/degerlendirme-kaydet",
    methods=["POST"]
)
@yonetici_gerekli
def degerlendirme_kaydet():

    try:

        veri = request.get_json()

        if not veri:

            return jsonify({
                "basarili": False,
                "mesaj":
                    "Veri alınamadı."
            }), 400

        try:

            calisma_id = int(
                veri.get("id")
            )

        except (
            TypeError,
            ValueError
        ):

            return jsonify({
                "basarili": False,
                "mesaj":
                    "Çalışma ID geçersiz."
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

        except (
            TypeError,
            ValueError
        ):

            return jsonify({
                "basarili": False,
                "mesaj":
                    "Puanlardan biri geçersiz."
            }), 400

        yorum = str(
            veri.get(
                "yorum",
                ""
            )
        ).strip()

        gecerli_puanlar = [
            5,
            10,
            15,
            20
        ]

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
                    "mesaj":
                        "Geçersiz puan gönderildi."
                }), 400

        toplam = (
            kompozisyon
            + oran_oranti
            + perspektif
            + isik_golge
            + cizgi_kullanimi
        )

        conn = sqlite3.connect(
            DATABASE
        )

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
                "mesaj":
                    "Çalışma bulunamadı."
            }), 404

        fotograf =
            kayit["fotograf"]

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

        if not kontrol:

            return jsonify({
                "basarili": False,
                "mesaj":
                    "Kayıt güncellendi ancak tekrar okunamadı."
            }), 500

        if kontrol["durum"] != "Değerlendirildi":

            return jsonify({
                "basarili": False,
                "mesaj":
                    "Değerlendirme kaydedilemedi."
            }), 500

        # Değerlendirilen fotoğrafı sil

        if fotograf:

            dosya_yolu = os.path.join(
                app.config["UPLOAD_FOLDER"],
                fotograf
            )

            if os.path.exists(
                dosya_yolu
            ):

                try:

                    os.remove(
                        dosya_yolu
                    )

                except Exception as e:

                    print(
                        "Fotoğraf silinemedi:",
                        str(e)
                    )

        return jsonify({

            "basarili":
                True,

            "mesaj":
                "Değerlendirme başarıyla kaydedildi.",

            "toplam":
                toplam

        })

    except Exception as e:

        print(
            "DEĞERLENDİRME HATASI:",
            str(e)
        )

        return jsonify({

            "basarili":
                False,

            "mesaj":
                f"Sunucu hatası: {str(e)}"

        }), 500


# ==================================================
# SUNUCU
# ==================================================

if __name__ == "__main__":

    print()
    print(
        "DETAY SANAT AKADEMİ sunucusu başlıyor..."
    )
    print(
        "Bilgisayardan:"
        " http://127.0.0.1:5000"
    )
    print(
        "Telefondan:"
        " http://192.168.0.18:5000"
    )
    print(
        "Yönetici:"
        " http://127.0.0.1:5000/yonetici-giris"
    )
    print()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
```
