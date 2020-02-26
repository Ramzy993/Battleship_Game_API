from http import HTTPStatus

from flask import Flask, jsonify, request
from .controllers.game_handler import GameHandler

app = Flask(__name__)

game_handler = GameHandler()


@app.route('/battleship', methods=['POST'])
def create_battleship_game():
    game_handler.flush()
    request_data = request.get_json()
    game_created_correctly = game_handler.execute_post(request_data['ships'])
    if not game_created_correctly:
        return jsonify(message="Please, check request data"), HTTPStatus.BAD_REQUEST
    return jsonify(message="Game created successfully"), HTTPStatus.OK


@app.route('/battleship', methods=['PUT'])
def shot():
    if len(game_handler.ships) == 0:
        return jsonify(message="Please, create game first."), HTTPStatus.BAD_REQUEST
    request_data = request.get_json()
    hit_sink_water_none = game_handler.execute_put(request_data)
    if not hit_sink_water_none:
        return jsonify(message="Please, check shot location"), HTTPStatus.BAD_REQUEST
    return jsonify(result=game_handler.result), HTTPStatus.OK


@app.route('/battleship', methods=['DELETE'])
def delete_battleship_game():
    game_handler.flush()
    return jsonify(message="Game Ended"), HTTPStatus.OK
