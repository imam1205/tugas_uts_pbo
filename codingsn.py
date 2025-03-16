import mysql.connector
from datetime import datetime

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="zakat_db"
    )

def setup_database():
    try:
        db = connect_db()
        cursor = db.cursor()
        
        # Create master_muzakki table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS master_muzakki (
                id_muzakki VARCHAR(20) PRIMARY KEY,
                nama VARCHAR(100),
                alamat TEXT,
                no_hp VARCHAR(15)
            )
        """)
        
        # Create master_beras table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS master_beras (
                id_beras INT AUTO_INCREMENT PRIMARY KEY,
                jenis_beras VARCHAR(50),
                harga_per_kg DECIMAL(10,2)
            )
        """)
        
        # Create transaksi_zakat table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transaksi_zakat (
                id_transaksi INT AUTO_INCREMENT PRIMARY KEY,
                id_muzakki VARCHAR(20),
                tanggal DATETIME,
                jumlah_jiwa INT,
                jenis_pembayaran ENUM('beras', 'uang'),
                jumlah_pembayaran DECIMAL(10,2),
                id_beras INT,
                FOREIGN KEY (id_muzakki) REFERENCES master_muzakki(id_muzakki),
                FOREIGN KEY (id_beras) REFERENCES master_beras(id_beras)
            )
        """)
        
        db.commit()
        print("Database setup successful!")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()

def tambah_muzakki():
    try:
        db = connect_db()
        cursor = db.cursor()
        
        print("\n=== Tambah Data Muzakki ===")
        id_muzakki = input("Masukkan ID Muzakki: ")
        nama = input("Masukkan Nama: ")
        alamat = input("Masukkan Alamat: ")
        no_hp = input("Masukkan No HP: ")
        
        sql = "INSERT INTO master_muzakki VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (id_muzakki, nama, alamat, no_hp))
        db.commit()
        print("Data muzakki berhasil ditambahkan!")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()

def tambah_beras():
    try:
        db = connect_db()
        cursor = db.cursor()
        
        print("\n=== Tambah Jenis Beras ===")
        jenis_beras = input("Masukkan Jenis Beras: ")
        harga = float(input("Masukkan Harga per Kg: "))
        
        sql = "INSERT INTO master_beras (jenis_beras, harga_per_kg) VALUES (%s, %s)"
        cursor.execute(sql, (jenis_beras, harga))
        db.commit()
        print("Data beras berhasil ditambahkan!")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()

def bayar_zakat():
    try:
        db = connect_db()
        cursor = db.cursor()
        
        print("\n=== Pembayaran Zakat Fitrah ===")
        id_muzakki = input("Masukkan ID Muzakki: ")
        jumlah_jiwa = int(input("Masukkan Jumlah Jiwa: "))
        jenis_pembayaran = input("Jenis Pembayaran (beras/uang): ").lower()
        
        if jenis_pembayaran == 'beras':
            # Tampilkan daftar beras
            cursor.execute("SELECT * FROM master_beras")
            beras_list = cursor.fetchall()
            print("\nDaftar Jenis Beras:")
            for beras in beras_list:
                print(f"{beras[0]}. {beras[1]} - Rp{beras[2]} per kg")
            
            id_beras = int(input("Pilih ID Beras: "))
            jumlah_pembayaran = 2.5 * jumlah_jiwa  # 2.5 kg per jiwa
            
        else:  # pembayaran uang
            cursor.execute("SELECT harga_per_kg FROM master_beras WHERE id_beras = 1")
            harga_beras = cursor.fetchone()[0]
            jumlah_pembayaran = 2.5 * jumlah_jiwa * harga_beras
            id_beras = None
        
        sql = """
            INSERT INTO transaksi_zakat 
            (id_muzakki, tanggal, jumlah_jiwa, jenis_pembayaran, jumlah_pembayaran, id_beras)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            id_muzakki,
            datetime.now(),
            jumlah_jiwa,
            jenis_pembayaran,
            jumlah_pembayaran,
            id_beras
        ))
        db.commit()
        print("Pembayaran zakat berhasil dicatat!")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()

