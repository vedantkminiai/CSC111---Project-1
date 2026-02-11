"""CSC111 Project 1: Text Adventure Game - Simulator

Instructions (READ THIS FIRST!)
===============================

This Python module contains code for Project 1 that allows a user to simulate
an entire playthrough of the game. Please consult the project handout for
instructions and details.

You can copy/paste your code from Assignment 1 into this file, and modify it as
needed to work with your game.

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
from event_logger import Event, EventList
from adventure import AdventureGame
from game_entities import Location


class AdventureGameSimulation:
    """A simulation of an adventure game playthrough.
    """
    # Private Instance Attributes:
    #   - _game: The AdventureGame instance that this simulation uses.
    #   - _events: A collection of the events to process during the simulation.
    _game: AdventureGame
    _events: EventList

    def __init__(self, game_data_file: str, initial_location_id: int, commands: list[str]) -> None:
        """
        Initialize a new game simulation based on the given game data, that runs through the given commands.

        Preconditions:
        - len(commands) > 0
        - all commands in the given list are valid commands when starting from the location at initial_location_id
        """
        self._events = EventList()
        self._game = AdventureGame(game_data_file, initial_location_id)

        current_location = self._game.get_location()
        first_event = Event(current_location.id_num, current_location.brief_description)
        self._events.add_event(first_event)

        self.generate_events(commands, current_location)

    def generate_events(self, commands: list[str], current_location: Location) -> None:
        """
        Generate events in this simulation, based on current_location and commands, a valid list of commands.

        Preconditions:
        - len(commands) > 0
        - all commands in the given list are valid commands when starting from current_location
        """

        for command in commands:
            if command in ["look", "inventory", "score", "log", "quit", "undo"]:
                if command == "undo":
                    next_loc_id = self._events.last.prev.id_num
                    self._events.remove_last_event()
                else:
                    next_loc_id = current_location.id_num
            elif command.startswith("take ") or command.startswith("deposit "):
                next_loc_id = current_location.id_num
            else:
                next_loc_id = current_location.available_commands[command]
            current_location = self._game.get_location(next_loc_id)
            brief_description = current_location.brief_description
            event = Event(next_loc_id, brief_description)
            self._events.add_event(event, command)

    def get_id_log(self) -> list[int]:
        """
        Get back a list of all location IDs in the order that they are visited within a game simulation
        that follows the given commands.
        """
        # Note: We have completed this method for you. Do NOT modify it for A1.

        return self._events.get_id_log()

    def run(self) -> None:
        """
        Run the game simulation and log location descriptions.
        """
        # Note: We have completed this method for you. Do NOT modify it for A1.

        current_event = self._events.first  # Start from the first event in the list

        while current_event:
            print(current_event.description)
            if current_event is not self._events.last:
                print("You choose:", current_event.next_command)

            # Move to the next event in the linked list
            current_event = current_event.next


if __name__ == "__main__":
    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (Delete the "#" and space before each line.)
    # IMPORTANT: keep this code indented inside the "if __name__ == '__main__'" block
    import python_ta

    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['R1705', 'E9998', 'E9999', 'static_type_checker']
    })

    #  a walkthrough of commands needed to win the game
    win_walkthrough = ["go east", "go south", "take usb drive", "go north", "go east", "go east", "take lucky mug",
                       "go west", "go west", "go north", "go east", "take laptop charger", "go west", "go south",
                       "go west", "deposit usb drive", "deposit laptop charger",
                       "deposit lucky mug"]  # a list of all the commands needed to walk through the game to win it
    expected_log = [1, 4, 5, 5, 4, 7, 8, 8, 7, 4, 3, 6, 6, 3, 4, 1, 1, 1,
                    1]  # the IDs of all locations that would be visited
    sim = AdventureGameSimulation('game_data.json', 1, win_walkthrough)
    assert expected_log == sim.get_id_log()

    #  a walkthrough of commands needed to win the game
    lose_demo = ["go east", "go south", "go north", "go east", "go east", "go west", "go west", "go north", "go north",
                 "go south", "go east", "go west", "go south", "go south", "go north", "go west", "go east", "go west",
                 "go east", "go west"]
    expected_log = [1, 4, 5, 4, 7, 8, 7, 4, 3, 2, 3, 6, 3, 4, 5, 4, 1, 4, 1, 4,
                    1]  # the IDs of all locations that would be visited
    sim = AdventureGameSimulation('game_data.json', 1, lose_demo)
    assert expected_log == sim.get_id_log()

    #  walkthroughs that show off the "inventory" command
    inventory_demo = ["go east", "go south", "take usb drive", "inventory", "go north", "go west", "deposit usb drive",
                      "inventory"]
    expected_log = [1, 4, 5, 5, 5, 4, 1, 1, 1]
    sim = AdventureGameSimulation('game_data.json', 1, inventory_demo)
    assert expected_log == sim.get_id_log()

    #  walkthroughs that show off the "score" command
    scores_demo = ["go east", "go south", "take usb drive", "go north", "go west", "deposit usb drive"]
    expected_log = [1, 4, 5, 5, 4, 1, 1]
    sim = AdventureGameSimulation('game_data.json', 1, scores_demo)
    assert expected_log == sim.get_id_log()

    # undo command demo
    enhancement1_demo = ["go east", "go north", "undo", "go north", "take toonie", "undo", "take toonie"]
    expected_log = [1, 4, 4, 3, 3, 3]
    sim = AdventureGameSimulation('game_data.json', 1, enhancement1_demo)
    print(sim.get_id_log())
    assert expected_log == sim.get_id_log()
