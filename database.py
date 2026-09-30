import sqlite3

DATABASE = "detay_sanat.db"


def veritabani_olustur():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Öğrenciler tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ogrenciler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ogrenci_kodu TEXT UNIQUE NOT NULL,
            ad_soyad TEXT NOT NULL
        )
    """)

    # Çalışmalar tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS calismalar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ogrenci_adi TEXT NOT NULL,
            calisma_turu TEXT,
            fotograf TEXT NOT NULL,
            durum TEXT DEFAULT 'Bekliyor',
            kompozisyon INTEGER,
            oran_oranti INTEGER,
            perspektif INTEGER,
            isik_golge INTEGER,
            cizgi_kullanimi INTEGER,
            yorum TEXT,
            tarih DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Eski veritabanına öğrenci kodu alanını ekle
    cursor.execute("""
        PRAGMA table_info(calismalar)
    """)

    sutunlar = [
        sutun[1]
        for sutun in cursor.fetchall()
    ]

    if "ogrenci_kodu" not in sutunlar:

        cursor.execute("""
            ALTER TABLE calismalar
            ADD COLUMN ogrenci_kodu TEXT
        """)

    conn.commit()
    conn.close()


def calisma_ekle(
    ogrenci_adi,
    calisma_turu,
    fotograf,
    ogrenci_kodu=None
):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO calismalar
        (
            ogrenci_adi,
            calisma_turu,
            fotograf,
            ogrenci_kodu
        )
        VALUES (?, ?, ?, ?)
    """, (
        ogrenci_adi,
        calisma_turu,
        fotograf,
        ogrenci_kodu
    ))

    conn.commit()

    yeni_id = cursor.lastrowid

    conn.close()

    return yeni_id


def ogrenci_ekle(
    ogrenci_kodu,
    ad_soyad
):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO ogrenciler
        (
            ogrenci_kodu,
            ad_soyad
        )
        VALUES (?, ?)
    """, (
        ogrenci_kodu,
        ad_soyad
    ))

    conn.commit()
    conn.close()


def ogrencileri_getir():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            ogrenci_kodu,
            ad_soyad
        FROM ogrenciler
        ORDER BY ad_soyad
    """)

    ogrenciler = cursor.fetchall()

    conn.close()

    return ogrenciler