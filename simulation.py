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

    # TODO: Copy/paste your code from A1, and make adjustments as needed
    def __init__(self, game_data_file: str, initial_location_id: int, commands: list[str]) -> None:
        """
        Initialize a new game simulation based on the given game data, that runs through the given commands.

        Preconditions:
        - len(commands) > 0
        - all commands in the given list are valid commands when starting from the location at initial_location_id
        """
        self._events = EventList()
        self._game = AdventureGame(game_data_file, initial_location_id)

        # TODO: Add first event (initial location, no previous command)
        # Hint: self._game.get_location() gives you back the current location
        current_location = self._game.get_location()
        first_event = Event(current_location.id_num, current_location.brief_description)
        self._events.add_event(first_event)

        # TODO: Generate the remaining events based on the commands and initial location
        # Hint: Call self.generate_events with the appropriate arguments
        self.generate_events(commands, current_location)

    def generate_events(self, commands: list[str], current_location: Location) -> None:
        """
        Generate events in this simulation, based on current_location and commands, a valid list of commands.

        Preconditions:
        - len(commands) > 0
        - all commands in the given list are valid commands when starting from current_location
        """

        # TODO: Complete this method as specified. For each command, generate the event and add it to self._events.
        # Hint: current_location.available_commands[command] will return the next location ID
        # which executing <command> while in <current_location_id> leads to
        for command in commands:
            if command.startswith("take ") or command.startswith("deposit "):
                next_loc_id = current_location.id_num
            elif command in ["look", "inventory", "score", "log", "quit", "undo"]:
                if command == "undo":
                    self._events.remove_last_event()
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
    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'disable': ['R1705', 'E9998', 'E9999', 'static_type_checker']
    # })

    # TODO: Modify the code below to provide a walkthrough of commands needed to win and lose the game
    win_walkthrough = ["go east", "go south", "take usb drive", "go north", "go east", "go east", "take lucky mug",
                       "go west", "go west", "go north", "go east", "take laptop charger", "go west", "go south",
                       "go west", "deposit usb drive", "deposit laptop charger",
                       "deposit lucky mug"]  # a list of all the commands needed to walk through the game to win it
    expected_log = [1, 4, 5, 5, 4, 7, 8, 8, 7, 4, 3, 6, 6, 3, 4, 1, 1, 1,
                    1]  # Update this log list to include the IDs of all locations that would be visited
    # Uncomment the line below to test your walkthrough
    sim = AdventureGameSimulation('game_data.json', 1, win_walkthrough)
    assert expected_log == sim.get_id_log()

    # Create a list of all the commands needed to walk through your game to reach a 'game over' state
    lose_demo = ["go east", "go south", "go north", "go east", "go east", "go west", "go west", "go north", "go north",
                 "go south", "go east", "go west", "go south", "go south", "go north", "go west", "go east", "go west",
                 "go east", "go west"]
    expected_log = [1, 4, 5, 4, 7, 8, 7, 4, 3, 2, 3, 6, 3, 4, 5, 4, 1, 4, 1, 4,
                    1]  # Update this log list to include the IDs of all locations that would be visited
    # Uncomment the line below to test your demo
    sim = AdventureGameSimulation('game_data.json', 1, lose_demo)
    assert expected_log == sim.get_id_log()

    # TODO: Add code below to provide walkthroughs that show off certain features of the game
    # TODO: Create a list of commands involving visiting locations, picking up items, and then
    #   checking the inventory, your list must include the "inventory" command at least once
    inventory_demo = ["go east", "go south", "take usb drive", "inventory", "go north", "go west", "deposit usb drive",
                      "inventory"]
    expected_log = [1, 4, 5, 5, 5, 4, 1, 1, 1]
    sim = AdventureGameSimulation('game_data.json', 1, inventory_demo)
    assert expected_log == sim.get_id_log()

    scores_demo = ["go east", "go north", "take toonie", "undo", "take toonie", "go north", "deposit toonie", "score"]
    expected_log = [1, 4, 3, 3, 3, 2, 2, 2]
    sim = AdventureGameSimulation('game_data.json', 1, scores_demo)
    assert expected_log == sim.get_id_log()

    # Add more enhancement_demos if you have more enhancements
    # undo command demo
    enhancement1_demo = ["go east", "go north", "undo"]
    expected_log = [1, 4, 3]
    sim = AdventureGameSimulation('game_data.json', 1, enhancement1_demo)
    assert expected_log == sim.get_id_log()

    # Note: You can add more code below for your own testing purposes
