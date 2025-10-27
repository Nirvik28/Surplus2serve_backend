from flask import Blueprint, request, jsonify, session
from BACKEND.models import FoodPost, User 
from BACKEND.db import db


bp = Blueprint('food', __name__)  # FIXED _name_ -> __name__

@bp.route('', methods=['POST'])
def add_food():
    if 'user_id' not in session:
        return jsonify({'error': 'Login required'}), 401
    user = User.query.get(session['user_id'])
    if user.role != 'restaurant':
        return jsonify({'error': 'Only restaurants can post food'}), 403

    data = request.get_json()
    food_post = FoodPost(
        food=data.get('food'),
        category=data.get('category'),
        quantity=data.get('quantity'),
        expiry_time=data.get('expiryTime'),
        location=data.get('location'),
        description=data.get('description'),
        allergens=data.get('allergens'),
        restaurant_id=user.id,
        status='available'
    )
    db.session.add(food_post)
    db.session.commit()
    return jsonify({'message': 'Food posted', 'id': food_post.id})

@bp.route('', methods=['GET'])
def get_foods():
    food_posts = FoodPost.query.order_by(FoodPost.posted_at.desc()).all()
    result = []
    for f in food_posts:
        result.append({
            'id': f.id,
            'food': f.food,
            'category': f.category,
            'quantity': f.quantity,
            'expiryTime': f.expiry_time,
            'location': f.location,
            'description': f.description,
            'allergens': f.allergens,
            'status': f.status,
            'postedAt': f.posted_at.isoformat(),
            'restaurant': User.query.get(f.restaurant_id).name if f.restaurant_id else 'Unknown',
            'claimedBy': User.query.get(f.claimed_by_id).name if f.claimed_by_id else None,
        })
    return jsonify(result)

@bp.route('/claim', methods=['POST'])
def claim_food():
    if 'user_id' not in session:
        return jsonify({'error': 'Login required'}), 401
    user = User.query.get(session['user_id'])
    if user.role not in ['ngo', 'volunteer']:
        return jsonify({'error': 'Only NGO or Volunteer can claim food'}), 403
    data = request.get_json()
    food_id = data.get('id')
    food_post = FoodPost.query.get(food_id)
    if not food_post or food_post.status != 'available':
        return jsonify({'error': 'Food not available'}), 404
    food_post.status = 'claimed'
    food_post.claimed_by_id = user.id
    db.session.commit()
    return jsonify({'message': 'Food claimed', 'id': food_post.id})
