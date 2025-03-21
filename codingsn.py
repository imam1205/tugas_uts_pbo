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
        # Validate Muzakki ID first
        while True:
            id_muzakki = input("Masukkan ID Muzakki: ")
            cursor.execute("SELECT nama FROM master_muzakki WHERE id_muzakki = %s", (id_muzakki,))
            result = cursor.fetchone()
            
            if result:
                print(f"Muzakki ditemukan: {result[0]}")
                break
            else:
                print("ID Muzakki tidak terdaftar! Silahkan masukkan ID yang benar.")
                pilihan = input("Ingin mencoba lagi? (y/n): ").lower()
                if pilihan != 'y':
                    print("Pembayaran dibatalkan.")
                    return

        jumlah_jiwa = int(input("Masukkan Jumlah Jiwa: "))
        jenis_pembayaran = input("Jenis Pembayaran (beras/uang): ").lower()
        
        # Konstanta zakat per jiwa (dalam liter)
        ZAKAT_PER_JIWA_LITER = 3.5  # 3.5 liter per jiwa
        
        if jenis_pembayaran == 'beras':
            # Tampilkan daftar beras
            cursor.execute("SELECT * FROM master_beras")
            beras_list = cursor.fetchall()
            print("\nDaftar Jenis Beras:")
            for beras in beras_list:
                # Harga per liter = harga per kg * 0.8 (konversi kg ke liter)
                harga_per_liter = float(beras[2]) * 0.8
                print(f"{beras[0]}. {beras[1]} - Rp{harga_per_liter:.2f} per liter")
            
            id_beras = int(input("Pilih ID Beras: "))
            jumlah_pembayaran = ZAKAT_PER_JIWA_LITER * jumlah_jiwa  # dalam liter
            print(f"Total pembayaran: {jumlah_pembayaran:.1f} liter")
            
        else:  # pembayaran uang
            cursor.execute("SELECT harga_per_kg FROM master_beras WHERE id_beras = 1")
            harga_beras = cursor.fetchone()[0]
            # Konversi ke harga per liter dan hitung total
            harga_per_liter = harga_beras * 0.8  # 1 kg beras ≈ 0.8 liter
            jumlah_pembayaran = ZAKAT_PER_JIWA_LITER * jumlah_jiwa * harga_per_liter
            print(f"Total pembayaran: Rp{jumlah_pembayaran:,.2f}")
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

def lihat_history():
    try:
        db = connect_db()
        cursor = db.cursor()
        
        print("\n=== History Pembayaran Zakat ===")
        sql = """
            SELECT t.*, m.nama, b.jenis_beras
            FROM transaksi_zakat t
            JOIN master_muzakki m ON t.id_muzakki = m.id_muzakki
            LEFT JOIN master_beras b ON t.id_beras = b.id_beras
        """
        cursor.execute(sql)
        hasil = cursor.fetchall()
        
        for row in hasil:
            print(f"\nID Transaksi: {row[0]}")
            print(f"Nama Muzakki: {row[7]}")
            print(f"Tanggal: {row[2]}")
            print(f"Jumlah Jiwa: {row[3]}")
            print(f"Jenis Pembayaran: {row[4]}")
            print(f"Jumlah Pembayaran: {row[5]}")
            if row[8]:
                print(f"Jenis Beras: {row[8]}")
            print("-" * 30)
            
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()

def main():
    setup_database()
    
    while True:
        print("\n=== Menu Zakat Fitrah ===")
        print("1. Tambah Data Muzakki")
        print("2. Tambah Jenis Beras")
        print("3. Bayar Zakat")
        print("4. Lihat History")
        print("5. Keluar")
        
        pilihan = input("\nPilih menu (1-5): ")
        
        if pilihan == '1':
            tambah_muzakki()
        elif pilihan == '2':
            tambah_beras()
        elif pilihan == '3':
            bayar_zakat()
        elif pilihan == '4':
            lihat_history()
        elif pilihan == '5':
            print("Program selesai!")
            break
        else:
            print("Pilihan tidak valid!")

if __name__ == "__main__":
    main()