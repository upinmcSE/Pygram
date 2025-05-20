from flask import Blueprint, request
from app import db
from app.utils import api_response, token_required
from app.models.post import Post
from app.models.like import Like
from app.models.follow import Follow

post_bp = Blueprint('post', __name__)

@post_bp.route('', methods=['POST'])
@token_required
def create_post(current_user):
    """UC7:API to create a new post."""

    data = request.get_json() or {}
    caption = data.get('caption')
    image_url = data.get('image_url')
    
    if image_url is None:
        return api_response(message="Image is required", status=400)
    
    try:
        post = Post(
            image_url=image_url,
            caption=caption,
            user_id=current_user.id
        )
        
        db.session.add(post)
        db.session.commit()
        
        return api_response(
            message="Create post successfully",
            data=post.to_dict(),
            status=201
        )
    except Exception as e:
        db.session.rollback()
        return api_response(message=f"Error creating post: {str(e)}", status=500)

@post_bp.route('/<int:post_id>', methods=['GET'])
@token_required
def get_post(current_user, post_id):
    """UC8: API xem chi tiết bài viết."""
    post = Post.query.get(post_id)
    
    if not post or post.deleted:
        return api_response(message="Post not found", status=404)
    
    post_data = post.to_dict()
    
    return api_response(data=post_data)

@post_bp.route('/', methods=['DELETE'])
@token_required
def delete_post(current_user, post_id):
    """UC09: Xóa bài viết (Delete Own Post)"""
    post = Post.query.get(post_id)
    
    if not post or post.deleted:
        return api_response(message="Post not found", status=404)
        
    if post.user_id != current_user.id:
        return api_response(message="Unauthorized to delete this post", status=403)
    
    try:
        post.deleted = True
        db.session.commit()
        return api_response(message="Post deleted successfully")
    except Exception as e:
        db.session.rollback()
        return api_response(message=f"Error deleting post: {str(e)}", status=500)

@post_bp.route('/<int:post_id>/like', methods=['POST'])
@token_required
def like_post(current_user, post_id):
    '''UC14: Thích bài viết (Like Post)'''
    post = Post.query.get(post_id)

    if not post or post.deleted:
        return api_response(message="Post not found", status=404)
    
    existing_like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    
    if existing_like:
        return api_response(message="Post already liked", status=400)
    
    try:
        new_like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(new_like)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return api_response(message=f"Error liking post: {str(e)}", status=500)
    return api_response(message="Liked post successfully")

@post_bp.route('/<int:post_id>/like', methods=['DELETE'])
@token_required
def unlike_post(current_user, post_id):
    like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    if not like:
        return api_response(message="Post not liked by this user", status=400)
    
    try:
        db.session.delete(like)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return api_response(message=f"Error unliking post: {str(e)}", status=500)
    return api_response(message="Unliked post successfully")

@post_bp.route('/newsfeed', methods=['GET'])
@token_required
def view_news_feed(current_user):
    """UC13: Xem News Feed (View News Feed)"""
    # Get pagination parameters from query string
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    current_user_id = current_user.id

    followed_records = Follow.query.filter_by(follower_id=current_user_id).all()

    followed_ids = [f.following_id for f in followed_records]

    followed_ids.append(current_user_id)
    
    # Get posts from database with pagination
    posts = Post.query.filter(
        Post.user_id.in_(followed_ids), 
        Post.deleted == False 
        ).order_by(Post.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)


    # Prepare response data
    response_data = {
        'items': [post.to_dict() for post in posts.items],
        'pagination': {
            'page': posts.page,
            'per_page': posts.per_page,
            'total': posts.total,
            'pages': posts.pages
        }
    }
    

    return api_response(data=response_data)