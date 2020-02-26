class GameHandler:
    _instances = None

    ships = {}
    board_locations = []
    result = "WATER"

    def __new__(cls):
        if not cls._instances:
            cls._instances = super().__new__(cls)
        return cls._instances

    def execute_post(self, payload_ships):
        ship_locations_are_correct = self._create_ships(payload_ships)
        if not ship_locations_are_correct:
            return False
        ship_is_not_overlapped = self._check_overlapped_ships()
        if not ship_is_not_overlapped:
            return False
        return True

    def execute_put(self, shot_location):
        location_out_of_border = self._check_location_out_of_game_borders(shot_location['x'], shot_location['y'])
        if location_out_of_border:
            return False
        self._update_location_status(shot_location['x'], shot_location['y'])
        return True

    def _create_ships(self, playload_ships):
        for ship in playload_ships:
            self.ships.update(
                {"ship_{}_{}".format(ship['x'], ship['y']): {
                    "size": ship['size'],
                    "orientation": ship['direction'],
                    "origin_x": ship['x'],
                    "origin_y": ship['y'],
                    "number_of_hits": 0,
                    "sink": False
                }})
            ship_locations_are_correct = self._create_ship_locations(ship['x'], ship['y'], ship['size'],
                                                                     ship['direction'])
            if not ship_locations_are_correct:
                return False
        return True

    def _create_ship_locations(self, origin_x, origin_y, size, orientation):
        if orientation == 'H':
            for x in range(origin_x, origin_x + size):
                out_of_game_border = self._check_location_out_of_game_borders(x, origin_y)
                if out_of_game_border:
                    return False
                self.board_locations.append([x, origin_y, 0, "ship_{}_{}".format(origin_x, origin_y)])
        else:
            for y in range(origin_y, origin_y + size):
                out_of_game_border = self._check_location_out_of_game_borders(origin_x, y)
                if out_of_game_border:
                    return False
                self.board_locations.append([origin_x, y, 0, "ship_{}_{}".format(origin_x, origin_y)])
        return True

    def _update_location_status(self, location_x, location_y):
        for location in self.board_locations:
            if (location[0], location[1]) == (location_x, location_y):
                if location[2]:
                    self.result = "HIT"
                    return
                location[2] = True
                sink_status = self._increment_number_of_hits_of_a_ship(location[3])
                if sink_status:
                    self.result = "SINK"
                    return
                self.result = "HIT"
                return
        self.result = "WATER"

    def _check_overlapped_ships(self):
        locations_list = [(location[0], location[1]) for location in self.board_locations]
        return len(locations_list) == len(set(locations_list))

    def _check_location_out_of_game_borders(self, location_x, location_y):
        return location_x < 0 or location_x > 9 or location_y < 0 or location_y > 9

    def _increment_number_of_hits_of_a_ship(self, ship_name):
        for ship_key, ship_value in self.ships.items():
            if ship_key == ship_name:
                ship_value["number_of_hits"] += 1
                return ship_value["number_of_hits"] == ship_value["size"]

    def flush(self):
        self.ships = {}
        self.board_locations = []
