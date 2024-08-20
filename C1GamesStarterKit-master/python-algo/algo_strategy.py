import gamelib
import random
import math
import warnings
from sys import maxsize
import json


"""
Most of the algo code you write will be in this file unless you create new
modules yourself. Start by modifying the 'on_turn' function.

Advanced strategy tips: 

  - You can analyze action frames by modifying on_action_frame function

  - The GameState.map object can be manually manipulated to create hypothetical 
  board states. Though, we recommended making a copy of the map to preserve 
  the actual current map state.
"""

class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        seed = random.randrange(maxsize)
        random.seed(seed)
        gamelib.debug_write('Random seed: {}'.format(seed))

    def on_game_start(self, config):
        """ 
        Read in config and perform any initial setup here 
        """
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config
        global WALL, SUPPORT, TURRET, SCOUT, DEMOLISHER, INTERCEPTOR, MP, SP
        WALL = config["unitInformation"][0]["shorthand"]
        SUPPORT = config["unitInformation"][1]["shorthand"]
        TURRET = config["unitInformation"][2]["shorthand"]
        SCOUT = config["unitInformation"][3]["shorthand"]
        DEMOLISHER = config["unitInformation"][4]["shorthand"]
        INTERCEPTOR = config["unitInformation"][5]["shorthand"]
        MP = 1
        SP = 0
        # This is a good place to do initial setup
        self.scored_on_locations = []
        # Stores all of the places we have already built a structure in as [[x: int, y: int, type: str, upgraded: 0/1]]
        self.built_structures = []
        # The iteration number we are of the defense lineup
        self.defense_iteration = 1
        # Defense iteration order
        self.defense_order = ["TURRET", "WALL", "FUNNEL", "SUPPORT"]
        # The index of the current defense stage we are supposed to be at
        self.intended_defense_stage = 0 


    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.GameState(self.config, turn_state)
        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
        game_state.suppress_warnings(True)  #Comment or remove this line to enable warnings.
        
        # Executes our custom strategy
        self.custom_strategy(game_state)

        game_state.submit_turn()

    """
    NOTE: This is where our algorithm begins, the code below is part of the provided starter-algo.    
    """

    def custom_strategy(self, game_state):
        # Execute setup if this is the first turn
        if game_state.turn_number == 1:
            self.execute_setup_formation(game_state)
        else:
            # Determine if anything needs to be rebuilt
            structure_points_after_rebuild = self.execute_rebuild(game_state)
            # Setup defenses if we have more than 1 structure point left
            if structure_points_after_rebuild > 1:
                self.execute_defense(game_state)
        # Setup attack
        self.execute_attack(game_state)
    
    def execute_setup_formation(self, game_state):
        turrets = [[14,11], [4,12], [23, 12]]
        walls = [[13,12], [15,12], [3,13], [5,13], [22, 13], [24, 13], [0,13], [27,13]]
        for turret in turrets:
            game_state.attempt_spawn(TURRET, [turret], 1)
            game_state.attempt_upgrade([turret])
            self.built_structures.append(turret[0], turret[1], TURRET, 1)
        for wall in walls:
            game_state.attempt_spawn(WALL, [wall], 1)
            self.built_structures.append(wall[0], wall[1], WALL, 0)

    def execute_rebuild(self, game_state):
        # Iterates through all of the built structures, checking if any of them need to be rebuilt
        # List allows us to maintain the priority that everything should be rebuilt in the order that it was built
        for structure in self.built_structures:
            x = structure[0]
            y = structure[1]
            type = structure[2]
            upgraded = structure[3]
            # Attemps to spawn structure
            game_state.attempt_spawn(type, [x, y], 1)
            # Attempts to upgrade structure if it was previously upgraded
            if upgraded:
                game_state.attempt_upgrade([x, y])
            # Gets own structure points, returns if we have 1 structure point left since that means we can't possibly do anything
            remaining_structure_points = game_state.get_resource(0, 0)
            if  remaining_structure_points <= 1:
                # Returns number of structure points remaning
                return remaining_structure_points
        # Returns number of structure points remaining
        return game_state.get_resource(0, 0)
    
    def execute_defense(self, game_state):
        # Constants for determining the order of defense gameplay
        current_defense_stage = self.intended_defense_stage
        # 
        intended_is_current = True
        # NEED TO REPLACE
        stockpiling = False
        iterations = 0
        # Iterates through defense moves until we have insufficient structure points to do anything
        while (game_state.get_resource(0,0) >= 2) and iterations < 10:
            # If only 2 structure points, we default to "WALL"
            structure_points = game_state.get_resource(0,0)
            if structure_points == 2:
                current_defense_stage = 1
                stage = "WALL"
            elif stockpiling:
                stage = "TURRET"
            else:
                stage = self.defense_order[current_defense_stage]
            if stage == "TURRET":
                succeeded = self.place_turrets(game_state)
            elif stage == "WALL":
                succeeded = self.place_walls(game_state)
            elif stage == "FUNNEL":
                succeeded = self.place_funnel(game_state)
            else:
                succeeded = self.place_support(game_state)
            iterations += 1
        gamelib.debug_write("HIT AN INFINITE LOOP ON DEFENSE ITERATIONS")

    def place_turrets(self, game_state) -> bool:
        pass

    def place_walls(self, game_state) -> bool:
        pass

    def place_funnel(self, game_state) -> bool:
        pass

    def place_support(self, game_state) -> bool:
        pass

    def execute_attack(self, game_state):
        # Determines whether or not we will be attacking
        attack = self.execute_attack_calculation(game_state)
        if (attack):
            # Do some placements of troops here
            return

    def execute_attack_calculation(game_state):
        # Calculate attack related stuff here
        pass
    
    def is_enemy_stockpiling(self):
        # Determine if the enemy is stockpiling (set to hard MP value)
        # TODO (julialding): if needed, calibrate a calculation for MP AND SP
        if self.get_resource(MP, 1) >= 8.5:
            return True
        return False
    
    def which_side_weaker(self):
        # TODO: calibrate
        TURRET_POINTS = 3
        UPGRADED_TURRET_POINTS = 8
        WALL_POINTS = 2

        def is_within_trapezoid(location, trapezoid):
            """ Checks if the given location is within the specified trapezoid. """
            x, y = location
            def is_point_in_trapezoid(x, y, trapezoid):
                def sign(p1, p2, p3):
                    return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
                
                b1 = sign([x, y], trapezoid[0], trapezoid[1]) < 0.0
                b2 = sign([x, y], trapezoid[1], trapezoid[2]) < 0.0
                b3 = sign([x, y], trapezoid[2], trapezoid[3]) < 0.0
                b4 = sign([x, y], trapezoid[3], trapezoid[0]) < 0.0
                
                return ((b1 == b2) and (b2 == b3) and (b3 == b4))
            
            return is_point_in_trapezoid(x, y, trapezoid)

        def calculate_area_value(trapezoid):
            score = 0
            for x in range(0, self.ARENA_SIZE):
                for y in range(0, self.ARENA_SIZE):
                    location = [x, y]
                    if self.in_arena_bounds(location) and is_within_trapezoid(location, trapezoid):
                        units = self[location]
                        for unit in units:
                            if unit.unit_type == 'TURRET':
                                score += TURRET_POINTS*unit.health
                            elif unit.unit_type == 'UPGRADED_TURRET':
                                score += UPGRADED_TURRET_POINTS*unit.health
                            elif unit.unit_type == 'WALL':
                                score += WALL_POINTS*unit.health
            return score

        # Define trapezoid vertices for left and right and center sides
        left_trapezoid = [[0, 13], [8, 13], [8, 10], [3, 10]]
        center_trapezoid = [[10, 7], [18, 7], [10, 13], [18, 13]]
        right_trapezoid = [[27, 13], [24, 10], [19, 10], [19, 13]]

        left_side_score = calculate_area_value(left_trapezoid)
        center_side_score = calculate_area_value(center_trapezoid)
        right_side_score = calculate_area_value(right_trapezoid)

        scores = [("L", left_side_score), ("C", center_side_score), ("R", right_side_score)]

        sorted_scores = sorted(scores, key=lambda x: x[1])

        ordered_labels = [label for label, _ in sorted_scores]

        return ordered_labels
        

    """
    NOTE: All the methods after this point are part of the sample starter-algo
    strategy and can safely be replaced for your custom algo.
    """

    def starter_strategy(self, game_state):
        """
        For defense we will use a spread out layout and some interceptors early on.
        We will place turrets near locations the opponent managed to score on.
        For offense we will use long range demolishers if they place stationary units near the enemy's front.
        If there are no stationary units to attack in the front, we will send Scouts to try and score quickly.
        """
        # First, place basic defenses
        self.build_defences(game_state)
        # Now build reactive defenses based on where the enemy scored
        self.build_reactive_defense(game_state)

        # If the turn is less than 5, stall with interceptors and wait to see enemy's base
        if game_state.turn_number < 5:
            self.stall_with_interceptors(game_state)
        else:
            # Now let's analyze the enemy base to see where their defenses are concentrated.
            # If they have many units in the front we can build a line for our demolishers to attack them at long range.
            if self.detect_enemy_unit(game_state, unit_type=None, valid_x=None, valid_y=[14, 15]) > 10:
                self.demolisher_line_strategy(game_state)
            else:
                # They don't have many units in the front so lets figure out their least defended area and send Scouts there.

                # Only spawn Scouts every other turn
                # Sending more at once is better since attacks can only hit a single scout at a time
                if game_state.turn_number % 2 == 1:
                    # To simplify we will just check sending them from back left and right
                    scout_spawn_location_options = [[13, 0], [14, 0]]
                    best_location = self.least_damage_spawn_location(game_state, scout_spawn_location_options)
                    game_state.attempt_spawn(SCOUT, best_location, 1000)

                # Lastly, if we have spare SP, let's build some supports
                support_locations = [[13, 2], [14, 2], [13, 3], [14, 3]]
                game_state.attempt_spawn(SUPPORT, support_locations)

    def build_defences(self, game_state):
        """
        Build basic defenses using hardcoded locations.
        Remember to defend corners and avoid placing units in the front where enemy demolishers can attack them.
        """
        # Useful tool for setting up your base locations: https://www.kevinbai.design/terminal-map-maker
        # More community tools available at: https://terminal.c1games.com/rules#Download

        # Place turrets that attack enemy units
        turret_locations = [[0, 13], [27, 13], [8, 11], [19, 11], [13, 11], [14, 11]]
        # attempt_spawn will try to spawn units if we have resources, and will check if a blocking unit is already there
        game_state.attempt_spawn(TURRET, turret_locations)
        
        # Place walls in front of turrets to soak up damage for them
        wall_locations = [[8, 12], [19, 12]]
        game_state.attempt_spawn(WALL, wall_locations)
        # upgrade walls so they soak more damage
        game_state.attempt_upgrade(wall_locations)

    def build_reactive_defense(self, game_state):
        """
        This function builds reactive defenses based on where the enemy scored on us from.
        We can track where the opponent scored by looking at events in action frames 
        as shown in the on_action_frame function
        """
        for location in self.scored_on_locations:
            # Build turret one space above so that it doesn't block our own edge spawn locations
            build_location = [location[0], location[1]+1]
            game_state.attempt_spawn(TURRET, build_location)

    def stall_with_interceptors(self, game_state):
        """
        Send out interceptors at random locations to defend our base from enemy moving units.
        """
        # We can spawn moving units on our edges so a list of all our edge locations
        friendly_edges = game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_LEFT) + game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)
        
        # Remove locations that are blocked by our own structures 
        # since we can't deploy units there.
        deploy_locations = self.filter_blocked_locations(friendly_edges, game_state)
        
        # While we have remaining MP to spend lets send out interceptors randomly.
        while game_state.get_resource(MP) >= game_state.type_cost(INTERCEPTOR)[MP] and len(deploy_locations) > 0:
            # Choose a random deploy location.
            deploy_index = random.randint(0, len(deploy_locations) - 1)
            deploy_location = deploy_locations[deploy_index]
            
            game_state.attempt_spawn(INTERCEPTOR, deploy_location)
            """
            We don't have to remove the location since multiple mobile 
            units can occupy the same space.
            """

    def demolisher_line_strategy(self, game_state):
        """
        Build a line of the cheapest stationary unit so our demolisher can attack from long range.
        """
        # First let's figure out the cheapest unit
        # We could just check the game rules, but this demonstrates how to use the GameUnit class
        stationary_units = [WALL, TURRET, SUPPORT]
        cheapest_unit = WALL
        for unit in stationary_units:
            unit_class = gamelib.GameUnit(unit, game_state.config)
            if unit_class.cost[game_state.MP] < gamelib.GameUnit(cheapest_unit, game_state.config).cost[game_state.MP]:
                cheapest_unit = unit

        # Now let's build out a line of stationary units. This will prevent our demolisher from running into the enemy base.
        # Instead they will stay at the perfect distance to attack the front two rows of the enemy base.
        for x in range(27, 5, -1):
            game_state.attempt_spawn(cheapest_unit, [x, 11])

        # Now spawn demolishers next to the line
        # By asking attempt_spawn to spawn 1000 units, it will essentially spawn as many as we have resources for
        game_state.attempt_spawn(DEMOLISHER, [24, 10], 1000)

    def least_damage_spawn_location(self, game_state, location_options):
        """
        This function will help us guess which location is the safest to spawn moving units from.
        It gets the path the unit will take then checks locations on that path to 
        estimate the path's damage risk.
        """
        damages = []
        # Get the damage estimate each path will take
        for location in location_options:
            path = game_state.find_path_to_edge(location)
            damage = 0
            for path_location in path:
                # Get number of enemy turrets that can attack each location and multiply by turret damage
                damage += len(game_state.get_attackers(path_location, 0)) * gamelib.GameUnit(TURRET, game_state.config).damage_i
            damages.append(damage)
        
        # Now just return the location that takes the least damage
        return location_options[damages.index(min(damages))]

    def detect_enemy_unit(self, game_state, unit_type=None, valid_x = None, valid_y = None):
        total_units = 0
        for location in game_state.game_map:
            if game_state.contains_stationary_unit(location):
                for unit in game_state.game_map[location]:
                    if unit.player_index == 1 and (unit_type is None or unit.unit_type == unit_type) and (valid_x is None or location[0] in valid_x) and (valid_y is None or location[1] in valid_y):
                        total_units += 1
        return total_units
        
    def filter_blocked_locations(self, locations, game_state):
        filtered = []
        for location in locations:
            if not game_state.contains_stationary_unit(location):
                filtered.append(location)
        return filtered

    def on_action_frame(self, turn_string):
        """
        This is the action frame of the game. This function could be called 
        hundreds of times per turn and could slow the algo down so avoid putting slow code here.
        Processing the action frames is complicated so we only suggest it if you have time and experience.
        Full doc on format of a game frame at in json-docs.html in the root of the Starterkit.
        """
        # Let's record at what position we get scored on
        state = json.loads(turn_string)
        events = state["events"]
        breaches = events["breach"]
        for breach in breaches:
            location = breach[0]
            unit_owner_self = True if breach[4] == 1 else False
            # When parsing the frame data directly, 
            # 1 is integer for yourself, 2 is opponent (StarterKit code uses 0, 1 as player_index instead)
            if not unit_owner_self:
                gamelib.debug_write("Got scored on at: {}".format(location))
                self.scored_on_locations.append(location)
                gamelib.debug_write("All locations: {}".format(self.scored_on_locations))

if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
