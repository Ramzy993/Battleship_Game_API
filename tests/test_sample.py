from os import path
import unittest
import json

from battleship.api import app, game_handler
from boltfile import TESTS_DIR


class TestSampleClass(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['DEBUG'] = False
        self.app.config['TESTING'] = True
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

    def tearDown(self):
        game_handler.flush()
        self.app_context.pop()

    def _load_json_data(self, file_name):
        with open(path.join(TESTS_DIR, "json_test_data", file_name + '.txt')) as json_file:
            data = json.load(json_file)
        return data

    def test_game_created_with_OK(self):
        json_data = self._load_json_data('ships_with_good_setup')
        with self.client as c:
            response = c.post('/battleship', json=json_data)
            self.assertEqual(response.status_code, 200)

    def test_game_created_with_setup_even_h(self):
        json_data = self._load_json_data('ships_with_good_setup_even_h')
        with self.client as c:
            c.post('/battleship', json=json_data)
            locations = [(location[0], location[1])for location in game_handler.board_locations]
            self.assertEqual(locations, [(2, 1), (3, 1), (4, 1), (5, 1)])

    def test_game_created_with_setup_odd_h(self):
        json_data = self._load_json_data('ships_with_good_setup_odd_h')
        with self.client as c:
            c.post('/battleship', json=json_data)
            locations = [(location[0], location[1])for location in game_handler.board_locations]
            self.assertEqual(locations, [(2, 1), (3, 1), (4, 1)])

    def test_game_created_with_setup_even_v(self):
        json_data = self._load_json_data('ships_with_good_setup_even_v')
        with self.client as c:
            c.post('/battleship', json=json_data)
            locations = [(location[0], location[1]) for location in game_handler.board_locations]
            self.assertEqual(locations, [(2, 1), (2, 2), (2, 3), (2, 4)])

    def test_game_created_with_setup_odd_v(self):
        json_data = self._load_json_data('ships_with_good_setup_odd_v')
        with self.client as c:
            c.post('/battleship', json=json_data)
            locations = [(location[0], location[1]) for location in game_handler.board_locations]
            self.assertEqual(locations, [(2, 1), (2, 2), (2, 3)])

    def test_game_response_BAD_REQUEST_when_ships_overlapped(self):
        json_data = self._load_json_data('ships_with_overlapped_ones')
        with self.client as c:
            response = c.post('/battleship', json=json_data)
            self.assertEqual(response.status_code, 400)

    def test_game_response_BAD_REQUEST_when_ships_origin_out_of_border(self):
        json_data = self._load_json_data('ships_with_origin_out_of_border')
        with self.client as c:
            response = c.post('/battleship', json=json_data)
            self.assertEqual(response.status_code, 400)

    def test_game_response_BAD_REQUEST_when_ships_setup_out_of_border(self):
        json_data = self._load_json_data('ships_with_setup_out_of_border')
        with self.client as c:
            response = c.post('/battleship', json=json_data)
            self.assertEqual(response.status_code, 400)

    def test_shot_produce_water(self):
        json_data = self._load_json_data('ships_to_test_shot_response')
        with self.client as c:
            c.post('/battleship', json=json_data)
            response = c.put('/battleship', json={"x": 2, "y": 2})
            data = json.loads(response.get_data(as_text=True))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data["result"], "WATER")

    def test_shot_produce_hit_after_first_hit(self):
        json_data = self._load_json_data('ships_to_test_shot_response')
        with self.client as c:
            c.post('/battleship', json=json_data)
            response = c.put('/battleship', json={"x": 2, "y": 1})
            data = json.loads(response.get_data(as_text=True))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data["result"], "HIT")

    def test_shot_produce_hit_after_second_hit(self):
        json_data = self._load_json_data('ships_to_test_shot_response')
        with self.client as c:
            c.post('/battleship', json=json_data)
            response = c.put('/battleship', json={"x": 2, "y": 1})
            data = json.loads(response.get_data(as_text=True))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data["result"], "HIT")

    def test_shot_produce_sink(self):
        json_data = self._load_json_data('ships_to_test_shot_response')
        with self.client as c:
            c.post('/battleship', json=json_data)
            response = c.put('/battleship', json={"x": 2, "y": 1})
            data = json.loads(response.get_data(as_text=True))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data["result"], "HIT")
            response = c.put('/battleship', json={"x": 3, "y": 1})
            data = json.loads(response.get_data(as_text=True))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data["result"], "HIT")
            response = c.put('/battleship', json={"x": 4, "y": 1})
            data = json.loads(response.get_data(as_text=True))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data["result"], "SINK")

    def test_shot_produce_hit_if_ship_is_sink(self):
        json_data = self._load_json_data('ships_to_test_shot_response')
        with self.client as c:
            c.post('/battleship', json=json_data)
            c.put('/battleship', json={"x": 2, "y": 1})
            c.put('/battleship', json={"x": 3, "y": 1})
            c.put('/battleship', json={"x": 4, "y": 1})
            response = c.put('/battleship', json={"x": 2, "y": 1})
            data = json.loads(response.get_data(as_text=True))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data["result"], "HIT")

    def test_shot_produce_BAD_REQUEST_when_shot_out_of_x_border_plus(self):
        json_data = self._load_json_data('ships_to_test_shot_response')
        with self.client as c:
            c.post('/battleship', json=json_data)
            response = c.put('/battleship', json={"x": 10, "y": 1})
            self.assertEqual(response.status_code, 400)

    def test_shot_produce_BAD_REQUEST_when_shot_out_of_x_border_minus(self):
        json_data = self._load_json_data('ships_to_test_shot_response')
        with self.client as c:
            c.post('/battleship', json=json_data)
            response = c.put('/battleship', json={"x": -1, "y": 1})
            self.assertEqual(response.status_code, 400)

    def test_shot_produce_BAD_REQUEST_when_shot_out_of_y_border_minus(self):
        json_data = self._load_json_data('ships_to_test_shot_response')
        with self.client as c:
            c.post('/battleship', json=json_data)
            response = c.put('/battleship', json={"x": 1, "y": -1})
            self.assertEqual(response.status_code, 400)

    def test_shot_produce_BAD_REQUEST_when_shot_out_of_y_border_plus(self):
        json_data = self._load_json_data('ships_to_test_shot_response')
        with self.client as c:
            c.post('/battleship', json=json_data)
            response = c.put('/battleship', json={"x": 1, "y": 10})
            self.assertEqual(response.status_code, 400)

    def test_game_response_OK_after_DELETE_request(self):
        json_data = self._load_json_data('ships_with_good_setup')
        with self.client as c:
            c.post('/battleship', json=json_data)
            response = c.delete('/battleship')
            self.assertEqual(response.status_code, 200)


if __name__=="__main__":
    unittest.main()
