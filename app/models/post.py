from datetime import datetime
from app import db

class Post(db.Model):
    """Model cho bài đăng."""
    __tablename__ = 'posts'
    
    id = db.Column("id", db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    image_url = db.Column(db.String(255), nullable=True)
    caption = db.Column(db.String(1000), nullable=True)
    deleted = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: int(datetime.now().timestamp()), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: int(datetime.now().timestamp()), onupdate=lambda: int(datetime.now().timestamp()), nullable=False)
    
    def __repr__(self):
        return f''
    
    def to_dict(self, include_user=False, include_likes=False, current_user=None):
        """Chuyển đổi post thành dictionary để trả về qua API."""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'image_url': self.image_url,
            'caption': self.caption,
            'deleted': self.deleted,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        if include_user:
            user = User.query.get(self.user_id)
            data['user'] = user.to_dict()
            
        if include_likes:
            data['like_count'] = Like.query.filter_by(post_id=self.id).count()
            if current_user:
                data['liked_by_current_user'] = Like.query.filter_by(post_id=self.id, user_id=current_user.id).first() is not None
            else:
                data['liked_by_current_user'] = False
        return data