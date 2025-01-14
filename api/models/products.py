from ..utils import db
from datetime import datetime
from enum import Enum

class ProductCategory(Enum):
    iphone = 'iphone',
    samsung = 'samsung',
    huawei = 'huawei',
    tecno = 'tecno',
    infinix = 'infinix',
    itel = 'itel',
    nokia = 'nokia',
    sony = 'sony',
    lg = 'lg',
    htc = 'htc',
    blackberry = 'blackberry',
    motorola = 'motorola',
    google = 'google',
    xiaomi = 'xiaomi',
    oppo = 'oppo',
    vivo = 'vivo',
    oneplus = 'oneplus',
    redmi = 'redmi',
    realme = 'realme',
    lenovo = 'lenovo',
    

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    stock = db.Column(db.Integer, nullable=False, default=0)
    category = db.Column(db.Enum(ProductCategory), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.stock is None:
            self.stock = 0
    
    def save(self):
        db.session.add(self)
        db.session.commit()