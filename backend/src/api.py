import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
import sys
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()



## ROUTES

@app.route('/drinks')
def get_all_drinks():
    drinks = Drink.query.all()
    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in drinks]
    })



@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_all_drinks_detail(token):
    try:
        drink_detail = Drink.query.all()
        if len(drink_detail) == 0:
            abort(401)
        
        body = [find.long() for find in drink_detail]
        return jsonify({
            'sccusse': True,
            'drinks': body})
    except Exception as e:
        abort(401)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_create_new_drink(token):

    body = request.get_json()
    try:
        title = body['title']
        recipe = body['recipe']
        
        recipe = json.dumps(recipe)
        drink = Drink(title=title, recipe=recipe)
        
        drink.insert()
        
        if drink is None:
                abort(405)
    except Exception:
        abort(405)
    return jsonify({
        'success': True,
        'drink': [drink.long()]
    })



@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_one_drink(token, id):
    body = request.get_json()
    drink = Drink.query.filter(Drink.id == id).one_or_none()

    if not drink:
        abort(404)

    try:
        title = body.get('title')
        
        if title:
            drink.title = title

       
        drink.update()
    except BaseException:
        abort(400)

    return jsonify({
        'success': True, 
        'drinks': [drink.long()]}), 200

@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_one_drink(token, drink_id ):
    try:
        drink=Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink is None:
            abort(404)
        drink.delete()
    except:
        abort(400)
    return jsonify({
        'success':True,
        'drink':drink_id
    })


# Error Handling

@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        'success': False,
        'error': error.status_code,
        'message': error.error['description']
    }), error.status_code

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        'success': False,
        'error': 422,
        'message': 'unprocessable'
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'resource not found'
    }), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'bad request'
    }), 400


@app.errorhandler(409)
def conflict(error):
    return jsonify({
        'success': False,
        'error': 409,
        'message': 'rosource is already exist'
    }), 409


@app.errorhandler(401)
def not_authorize(error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': 'unathurize user'
    }), 401


@app.errorhandler(403)
def insufficient_permission(error):
    return jsonify({
        'success': False,
        'error': 403,
        'message': 'insufficient permission'
    }), 403