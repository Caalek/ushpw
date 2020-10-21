from ushpw import db
from datetime import datetime

class Random(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    short_id = db.Column(db.String(40), unique = True, nullable = False)
    long_url = db.Column(db.String(300), unique = False, nullable = False)
    clicks = db.Column(db.Integer, unique = False, nullable = False)
    created_on = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    
    def __repr__(self):
        return f"Random('{self.id}', '{self.short_id}', '{self.long_url}', {self.clicks}, {self.created_on})"

class Custom(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    short_id = db.Column(db.String(40), unique = True, nullable = False)
    long_url = db.Column(db.String(300), unique = False, nullable = False)
    clicks = db.Column(db.Integer, unique = False, nullable = False)
    created_on = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    
    def __repr__(self):
        return f"Custom('{self.id}', '{self.short_id}', '{self.long_url}', {self.clicks}, {self.created_on})"
