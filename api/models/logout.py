from ..utils import db
from datetime import datetime

class TokenBlockList(db.Model):
    __tablename__ = 'token_blocklist'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    jti = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    @classmethod
    def is_jti_blocklisted(cls, jti):
        return cls.query.filter_by(jti=jti).first() is not None