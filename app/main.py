import psycopg2
from fastapi import FastAPI, status, HTTPException
from random import randint
from . import schemas

app = FastAPI(title="Tabungan API")

try:
    conn = psycopg2.connect(
        host='localhost',
        database='tabungan',
        user='postgres',
        password='root'
    )
    cursor = conn.cursor()
    print("Database connection succesfull!")
except Exception as error:
    print("Database connection failed.")
    print("Error: ", error)


@app.get("/", tags=["Python Backend Assessment Test"])
def read_root():
    return {
        "creator": "Devanis Dwi Sutrisno",
        "message": "Welcome to my FastAPI"
    }

@app.post("/daftar", tags=["Daftar"], status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.User):
    
    no_rekening = ''.join(["{}".format(randint(0, 5)) for num in range(0, 5)])

    cursor.execute("""
        SELECT * from users
        where nik = %s or no_hp = %s
        """,
        (user.nik, user.no_hp,)
    )
    check_user = cursor.fetchone()
    if check_user:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=f"Data telah terdaftar.")

    cursor.execute("""
        INSERT INTO users (no_rekening, nama, nik, no_hp, saldo)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING *
    """, (no_rekening, user.nama, user.nik, user.no_hp, user.saldo,))
    conn.commit()
    return {
        "message": "Pendaftaran Berhasil!",
        "no_rekening": no_rekening
    }


@app.get("/saldo/{no_rekening}", tags=["Cek Saldo"])
def read_saldo(no_rekening: str):
    cursor.execute("""
        SELECT no_rekening, saldo FROM users WHERE no_rekening = %s""",
        (no_rekening,)
    )
    user = cursor.fetchone()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Nomor Rekening tidak terdaftar.")
    return user  


@app.post("/tabung", tags=["Isi Saldo"])
def create_tabungan(transaksi: schemas.TransaksiParam):
    cursor.execute("""
        SELECT saldo FROM users WHERE no_rekening = %s
    """, (transaksi.no_rekening,))
    saldo = cursor.fetchone()
    
    if not saldo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Nomor Rekening tidak terdaftar.")
    newSaldo = float(saldo[0]) + transaksi.nominal
    cursor.execute("""
        UPDATE users SET saldo = %s
        where no_rekening = %s
    """, (newSaldo,transaksi.no_rekening,))
    conn.commit()

    cursor.execute("""
        INSERT INTO mutations (user_no_rekening, kode_transaksi, nominal) VALUES (%s, 'C', %s)
    """, (transaksi.no_rekening,transaksi.nominal,))
    conn.commit()

    return {
        "no_rekening": transaksi.no_rekening,
        "saldo": newSaldo
    }


@app.post("/tarik", tags=["Tarik Saldo"])
def create_tarik(transaksi: schemas.TransaksiParam):
    cursor.execute("""
        SELECT saldo FROM users
        WHERE no_rekening = %s
        AND saldo > %s 
        AND saldo - %s > 50000
    """, (transaksi.no_rekening,transaksi.nominal,transaksi.nominal,))
    saldo = cursor.fetchone()
    
    if not saldo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Nomor Rekening tidak terdaftar.")
    
    newSaldo = float(saldo[0]) - transaksi.nominal
    cursor.execute("""
        UPDATE users SET saldo = %s
        where no_rekening = %s
    """, (newSaldo,transaksi.no_rekening,))
    conn.commit()

    cursor.execute("""
        INSERT INTO mutations (user_no_rekening, kode_transaksi, nominal) VALUES (%s, 'D', %s)
    """, (transaksi.no_rekening,transaksi.nominal,))
    conn.commit()

    return {
        "no_rekening": transaksi.no_rekening,
        "saldo": newSaldo
    }

@app.get("/mutasi/{user_no_rekening}", tags=["Mutasi Rekening"])
def read_mutasi(user_no_rekening: str):
    cursor.execute("""
        SELECT nominal FROM mutations WHERE user_no_rekening = %s
    """, (user_no_rekening,))
    mutasi = cursor.fetchone()
    
    if not mutasi:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Nomor Rekening tidak terdaftar.")

    cursor.execute("""
        SELECT * FROM mutations
    """)
    listMutasi = cursor.fetchall()
    return listMutasi

    

    