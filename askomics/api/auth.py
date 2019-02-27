"""Authentication routes
"""

from functools import wraps

from askomics.libaskomics.LocalAuth import LocalAuth

from flask import (Blueprint, current_app, jsonify, request, session)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        """Login required decorator
        """

        if 'user' in session:
            if not session['user']['blocked']:
                return f(*args, **kwargs)
            return jsonify({"error": True, "errorMessage": "Blocked account"})
        return jsonify({"error": True, "errorMessage": "Login required"}), 401

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        """Login required decorator
        """

        if 'user' in session:
            if session['user']['admin']:
                return f(*args, **kwargs)
            return jsonify({"error": True, "errorMessage": "Admin required"})
        return jsonify({"error": True, "errorMessage": "Login required"}), 401

    return decorated_function


@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Register a new user

    Returns
    -------
    json
        Info about the user
    """

    user = {}

    data = request.get_json()

    local_auth = LocalAuth(current_app, session)
    local_auth.check_inputs(data)

    if not local_auth.get_error():
        user = local_auth.persist_user(data)
        local_auth.create_user_directories(user['id'], user['username'])
        session['user'] = user

    return jsonify({
        'error': local_auth.get_error(),
        'errorMessage': local_auth.get_error_message(),
        'user': user
    })


@auth_bp.route('/login', methods=['POST'])
def login():
    """Log a user

    Returns
    -------
    json
        Information about the logged user
    """
    data = request.get_json()

    local_auth = LocalAuth(current_app, session)
    authentication = local_auth.authenticate_user(data)

    if not authentication['error']:
        session['user'] = authentication['user']

    return jsonify({
        'error': authentication['error'],
        'errorMessage': authentication['error_messages'],
        'user': authentication['user']
    })


@auth_bp.route('/profile', methods=['POST'])
@login_required
def update_profile():
    """Update user profile (names and email)

    Returns
    -------
    json
        The updated user
    """
    data = request.get_json()

    local_auth = LocalAuth(current_app, session)
    updated_user = local_auth.update_profile(data, session['user'])

    session['user'] = updated_user['user']

    return jsonify({
        'error': updated_user['error'],
        'errorMessage': updated_user['error_message'],
        'user': updated_user['user']
    })


@auth_bp.route('/password', methods=['POST'])
@login_required
def update_password():
    """Update the user passord

    Returns
    -------
    json
        The user
    """
    data = request.get_json()

    local_auth = LocalAuth(current_app, session)
    updated_user = local_auth.update_password(data, session['user'])

    return jsonify({
        'error': updated_user['error'],
        'errorMessage': updated_user['error_message'],
        'user': updated_user['user']
    })


@auth_bp.route('/apikey', methods=['GET'])
@login_required
def update_apikey():
    """Update the user apikey

    Returns
    -------
    json
        The user with his new apikey
    """
    local_auth = LocalAuth(current_app, session)
    updated_user = local_auth.update_apikey(session['user'])

    session['user'] = updated_user['user']

    return jsonify({
        'error': updated_user['error'],
        'errorMessage': updated_user['error_message'],
        'user': updated_user['user']
    })


@auth_bp.route('/logout', methods=['GET'])
def logout():
    """Logout the current user

    Returns
    -------
    json
        no username and logged false
    """
    session.pop('user', None)

    current_app.logger.debug(session)
    return jsonify({'user': {}, 'logged': False})