"""CSC111 Project 1: Text Adventure Game - Game Manager

Instructions (READ THIS FIRST!)
===============================

This Python module contains the code for Project 1. Please consult
the project handout for instructions and details.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2026 CSC111 Teaching Team
"""
from __future__ import annotations
import json
from typing import Optional

from pygame.examples.go_over_there import target_position

from game_entities import Location, Item
from event_logger import Event, EventList


# Note: You may add in other import statements here as needed

# Note: You may add helper functions, classes, etc. below as needed


class AdventureGame:
    """A text adventure game class storing all location, item and map data.

    Instance Attributes:
        - current_location_id: the ID of the location the game is currently in
        - inventory: inventory of the player
        - score: score the player has accumulated
        - moves: amount of moves the player has done
        - ongoing: whether the game is still ongoing
    Representation Invariants:
        - # TODO add any appropriate representation invariants as needed
    """

    # Private Instance Attributes (do NOT remove these two attributes):
    #   - _locations: a mapping from location id to Location object.
    #                       This represents all the locations in the game.
    #   - _items: a list of Item objects, representing all items in the game.

    _locations: dict[int, Location]
    _items: list[Item]
    current_location_id: int  # Suggested attribute, can be removed
    inventory: list[Item]
    score: int
    moves: int
    ongoing: bool  # Suggested attribute, can be removed

    def __init__(self, game_data_file: str, initial_location_id: int) -> None:
        """
        Initialize a new text adventure game, based on the data in the given file, setting starting location of game
        at the given initial location ID.
        (note: you are allowed to modify the format of the file as you see fit)

        Preconditions:
        - game_data_file is the filename of a valid game data JSON file
        """

        # NOTES:
        # You may add parameters/attributes/methods to this class as you see fit.

        # Requirements:
        # 1. Make sure the Location class is used to represent each location.
        # 2. Make sure the Item class is used to represent each item.

        # Suggested helper method (you can remove and load these differently if you wish to do so):
        self._locations, self._items = self._load_game_data(game_data_file)
        self.inventory = []
        self.score = 0
        self.moves = 0
        # Suggested attributes (you can remove and track these differently if you wish to do so):
        self.current_location_id = initial_location_id  # game begins at this location
        self.ongoing = True  # whether the game is ongoing

    @staticmethod
    def _load_game_data(filename: str) -> tuple[dict[int, Location], list[Item]]:
        """Load locations and items from a JSON file with the given filename and
        return a tuple consisting of (1) a dictionary of locations mapping each game location's ID to a Location object,
        and (2) a list of all Item objects."""

        with open(filename, 'r') as f:
            data = json.load(f)  # This loads all the data from the JSON file

        locations = {}
        for loc_data in data['locations']:  # Go through each element associated with the 'locations' key in the file
            location_obj = Location(loc_data['id'], loc_data['brief_description'], loc_data['long_description'],
                                    loc_data['available_commands'], loc_data['items'])
            locations[loc_data['id']] = location_obj

        items = []
        # YOUR CODE BELOW
        for item_data in data['items']:  # Go through each element associated with the 'locations' key in the file
            item_obj = Item(item_data['name'], item_data['start_position'], item_data['target_position'],
                            item_data['target_points'])
            items.append(item_obj)

        return locations, items

    def get_location(self, loc_id: Optional[int] = None) -> Location:
        """Return Location object associated with the provided location ID.
        If no ID is provided, return the Location object associated with the current location.
        """
        if loc_id is None:
            return self._locations[self.current_location_id]
        else:
            return self._locations[loc_id]

    def is_valid_choice(self, choice: str, location: Location, menu: list[str]) -> bool:
        """"Return whether choice is a valid choice"""
        if choice in menu:
            return True
        elif choice in location.available_commands:
            return True
        elif choice.startswith("take "):
            item_name = choice[5:0]  # slice "take " off choice to get the item's name
            return item_name in location.items
        elif choice.startswith("deposit "):
            item_name = choice[8:0]  # slice "deposit " off choice to get the item's name
            return any(itm.name == item_name and itm.target_position == location.id_num for itm in self.inventory)
        return False

    def take_item(self, loc_id: int, item_name: str) -> bool:
        """"Take an item from the given location and put it in the inventory.
        Return True if successful, False otherwise.
        """
        location = self._locations[loc_id]

        # Item must be at this location
        if item_name not in location.items:
            return False

        # Find the corresponding Item object
        for item in self._items:
            if item.name == item_name:
                location.items.remove(item_name)
                self.inventory.append(item)
                return True

        return False

    def deposit_item(self, loc_id: int, item_name: str) -> bool:
        """Attempt to deposit an item at the given location and take it out of the inventory.
        Return True if successful, False otherwise.
        """
        # current location must be the same as the provided location ID
        if loc_id != self.current_location_id:
            return False

        location = self._locations[loc_id]

        for item in self.inventory:
            if item.name == item_name and item.target_position == loc_id:
                self.inventory.remove(item)
                self.score += item.target_points
                location.items.append(item_name)
                return True

        return False


if __name__ == "__main__":
    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (Delete the "#" and space before each line.)
    # IMPORTANT: keep this code indented inside the "if __name__ == '__main__'" block
    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'disable': ['R1705', 'E9998', 'E9999', 'static_type_checker']
    # })

    DORM = 1
    MAX_MOVE = 30
    game_log = EventList()  # This is REQUIRED as one of the baseline requirements
    game = AdventureGame('game_data.json', 1)  # load data, setting initial location ID to 1
    menu = ["look", "inventory", "score", "log", "quit"]  # Regular menu options available at each location
    choice = None

    # Note: You may modify the code below as needed; the following starter code is just a suggestion
    while game.ongoing:
        # Note: If the loop body is getting too long, you should split the body up into helper functions
        # for better organization. Part of your mark will be based on how well-organized your code is.

        location = game.get_location()

        # TODO: Add new Event to game log to represent current game location
        #  Note that the <choice> variable should be the command which led to this event
        # YOUR CODE HERE
        event = Event(location.id_num, location.long_description)
        game_log.add_event(event, choice)

        # TODO: Depending on whether or not it's been visited before,
        #  print either full description (first time visit) or brief description (every subsequent visit) of location
        # YOUR CODE HERE
        if location.visited:
            print(f"LOCATION {location.id_num}\n{location.brief_description}")
        else:
            print(f"LOCATION {location.id_num}\n{location.long_description}")

        # Display possible actions at this location
        print("What to do? Choose from: look, inventory, score, log, quit")
        print("At this location, you can also:")
        for action in location.available_commands:
            print("-", action)

        # Display possible take at this location
        for item_name in location.items:
            print("-", f"take {item_name}")

        # Display possible deposit at this location
        for item in game.inventory:
            if item.target_position == location.id_num:
                print("-", f"deposit {item.name}")

        # Validate choice
        choice = input("\nEnter action: ").lower().strip()
        while not game.is_valid_choice(choice, location, menu):
            print("That was an invalid option; try again.")
            choice = input("\nEnter action: ").lower().strip()

        print("========")
        print("You decided to:", choice)

        if choice in menu:
            # TODO: Handle each menu command as appropriate
            if choice == "log":
                game_log.display_events()
            elif choice == "look":
                print(f"LOCATION {location.id_num}\n{location.long_description}")
            elif choice == "inventory":
                print("You are carrying: ")
                for item in game.inventory:
                    print("-", item)
            elif choice == "score":
                print("Current score:", game.score)
            else:
                print("YOU QUITTED")
                game.ongoing = False

        elif choice in location.available_commands:  # action that the location
            # TODO: Add in code to deal with special locations (e.g. puzzles) as needed for your game
            # Handle non-menu actions
            result = location.available_commands[choice]
            game.current_location_id = result
            game.moves += 1  # Go[direction] takes 1 move

        else:  # action that do not change the location
            # TODO: Add in code to deal with actions which do not change the location (e.g. taking or using an item)
            if choice.startswith("take "):
                item_name = choice[5:0]
                if game.take_item(location.id_num, item_name):
                    game.moves += 1
            elif choice.startswith("deposit "):
                item_name = choice[8:0]
                if game.deposit_item(location.id_num, item_name):
                    game.moves += 1

                # check if this location is the dorm and all 3 item are present (Win conditon)
                if location.id_num == DORM and all(
                        itm in location.items for itm in ["laptop charger", "lucky mug", "usb drive"]):
                    for i in range(0, game.score):
                        print("YOU WIN")
                    game.ongoing = False

        if game.moves == MAX_MOVE:  # Runs out of moves (Game Over)
            game.ongoing = False
            print("GAME OVER")
