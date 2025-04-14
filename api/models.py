from flask_sqlalchemy import SQLAlchemy

# Khởi tạo đối tượng SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    
    def __repr__(self):
        return f"<User {self.username}>"
