from pydantic import BaseModel
from datetime import datetime

# data model
class User(BaseModel):
    no_rekening: str = None
    nama: str
    nik: str
    no_hp: str
    saldo: float = 0

class Mutasi(BaseModel):
    user_no_rekening: str
    log: datetime
    kode_transaksi: str
    nominal: float

class TransaksiParam(BaseModel):
    no_rekening: str
    nominal: float