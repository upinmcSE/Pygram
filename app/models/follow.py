from datetime import datetime
from app import db

class Follow(db.Model):
    """Model cho chức năng theo dõi (follow) giữa các người dùng."""
    __tablename__ = 'follows'

    follower_id = db.Column('follower_id', db.Integer, primary_key=True)
    # ID of the user being followed
    following_id = db.Column('following_id', db.Integer, primary_key=True)
    created_at = db.Column('created_at', db.Integer, default=lambda: int(datetime.now().timestamp()))

    def __repr__(self):
        return f' {self.following_id}>'