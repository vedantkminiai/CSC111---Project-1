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

from game_entities import Location, Item
from event_logger import Event, EventList
import random


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
        - _locations != {}
        - all(id >= 0 for id in _locations)
        - all(id == _locations[id].id_num for id in _locations)
        - current_location_id in _locations
        - score >= 0
        - moves >= 0
        - all(item in _items for item in inventory)
        - all(not item.deposited for item in inventory)
    """
    # Private Instance Attributes (do NOT remove these two attributes):
    #   - _locations: a mapping from location id to Location object.
    #                       This represents all the locations in the game.
    #   - _items: a list of Item objects, representing all items in the game.

    _locations: dict[int, Location]
    _items: list[Item]
    current_location_id: int
    inventory: list[Item]
    score: int
    moves: int
    ongoing: bool

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
                                    loc_data['available_commands'], loc_data['items'], loc_data['puzzle_words'])
            locations[loc_data['id']] = location_obj

        items = []
        # YOUR CODE BELOW
        for item_data in data['items']:  # Go through each element associated with the 'locations' key in the file
            item_obj = Item(item_data['name'], item_data['description'], item_data['start_position'],
                            item_data['target_position'], item_data['target_points'], item_data['deposited'])
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

    def get_item(self, item_name: str) -> Item:
        """Return the Item object with the given name.

            Preconditions:
                - any(itm.name == item_name for itm in self._items)
        """
        for item in self._items:
            if item.name == item_name:
                return item

        raise ValueError(f"No item named {item_name}")

    def is_valid_choice(self, choice: str, location: Location, menu: list[str]) -> bool:
        """"Return whether choice is a valid choice"""
        if choice in menu:
            return True
        elif choice in location.available_commands:
            return True
        elif choice.startswith("take "):
            item_name = choice[5:]  # slice "take " off choice to get the item's name
            return item_name in location.items and not self.get_item(item_name).deposited
        elif choice.startswith("deposit "):
            item_name = choice[8:]  # slice "deposit " off choice to get the item's name
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
                location.items.remove(item_name)  # Remove item from location
                self.inventory.append(item)  # Add item to inventory
                print(item.description)  # Display the item description
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
                self.inventory.remove(item)  # Remove item from inventory
                item.deposited = True  # set item is deposited
                self.score += item.target_points  # score increase by item.target_points
                location.items.append(item_name)  # Add item to location
                return True

        return False

    def _undo_take_item(self, loc_id: int, item_name: str) -> bool:
        """Undo a previously executed take action.
        This method removes the specified item from the player's inventory and places it back into the given location.
        Return True if the undo was successful, and False otherwise.

            Preconditions:
                - loc_id is a valid location ID
                - item_name refers to an item that was previously taken
        """
        location = self._locations[loc_id]

        # find item object in inventory
        for item in self.inventory:
            if item.name == item_name:
                self.inventory.remove(item)
                location.items.append(item_name)
                return True
        return False

    def _undo_deposit_item(self, loc_id: int, item_name: str) -> bool:
        """Undo a previously executed deposit action.
        This method removes the specified item from the given location, restores it to the player's inventory,
        and reverses the score gained from depositing it.
        Return True if the undo was successful, and False otherwise.

            Preconditions:
                - loc_id is a valid location ID
                - item_name refers to an item that was previously deposited at this location
        """
        location = self._locations[loc_id]

        if item_name not in location.items:
            return False

        item = self.get_item(item_name)
        if item.target_position != loc_id:
            return False

        location.items.remove(item_name)
        self.inventory.append(item)
        item.deposited = False
        self.score -= item.target_points
        return True

    def undo_action(self, game_log: EventList) -> bool:
        """Undo the most recent non-menu player action.
        Undo only applies to movement and item actions (e.g., 'go ...', 'take ...', 'deposit ...').
        If the most recent action was a menu command, this returns False and does nothing.
        """
        previous_game_state = game_log.last.prev
        previous_location_id = previous_game_state.id_num
        command = previous_game_state.next_command

        location = self.get_location(previous_location_id)
        if command in location.available_commands:  # if the command changes location roll back to its previous location
            self.current_location_id = previous_location_id
            game_log.remove_last_event()
            self.moves -= 1
            return True
        elif command.startswith("take "):
            item_name = command[5:]
            if self._undo_take_item(previous_location_id, item_name):
                game_log.remove_last_event()
                self.moves -= 1
                return True
        elif command.startswith("deposit "):
            item_name = command[8:]
            if self._undo_deposit_item(previous_location_id, item_name):
                game_log.remove_last_event()
                self.moves -= 1
                return True
        return False

    @staticmethod
    def generate_word(location: Location):
        """Generate a word related to the location given for the simple puzzle game.
        Randomly selects a word from the specified locations puzzle word list.

            Preconditions:
            - location.puzzle_words != []
        """
        words = location.puzzle_words
        hangman = random.choice(words)
        return hangman

    # updates word after guessing a letter
    @staticmethod
    def update_word(new_hangman) -> str:
        """Converts list of characters back into a string after user guesses a letter
        """
        word_hidden = ""
        for i in new_hangman:
            word_hidden += i
        return word_hidden

    # main
    def puzzle(self, location: Location) -> bool:
        """Hangman puzzle game, the puzzle-solver guesses one letter a time to decode the puzzle word.
        The puzzle-solver has 10 tries to fully decode the puzzle before failing.
        If they've surpasssed 10 tries, then the option to retry is available.
        Required for players to obtain special required items.
        """
        y = True  # Boolean variable controlling the loop for the game
        while True:
            if not y:
                try_again = input("Would you like to try again? Enter y or n: ")
                if try_again == "y":
                    y = True
                    print()
                elif try_again == "n":
                    print("Puzzle Over")
                    return False
                else:
                    print("Invalid input")
            chosen_word = self.generate_word(location)
            new_hangman = []
            for i in chosen_word:
                new_hangman.append("*")
            tries = 0
            while y:
                updated_word = self.update_word(new_hangman)
                # Asks the user for a guess and checks if the guess is valid
                while True:
                    check = True
                    guess = input(f"(Guess) Enter a letter in word {updated_word}: ")
                    if len(guess) > 1:
                        print("Please enter 1 letter")
                        check = False
                    if not guess.isalpha():
                        print("Please enter a letter")
                        check = False
                    if check:
                        break
                tries += 1
                already = False # Checks and reveals if the letter is in word
                for i in range(len(chosen_word)):
                    if chosen_word[i] == guess and new_hangman[i] == guess:
                        already = True
                        tries -= 1
                    if chosen_word[i] == guess:
                        new_hangman[i] = guess  # Outputs if the letter was already entered
                if already:
                    print(f"    {guess} is already in the word")
                x = "*" in new_hangman  # If the user runs out of attempts before guessing the word fully
                if tries >= 10 and x:
                    print(f"You have failed the puzzle, the word was {chosen_word}\n")
                    y = False  # If the user guesses the word fully, outputs how many guesses it took
                if not x:
                    print(f"You've completed the puzzle! The word is {chosen_word}. You missed {tries} time(s)\n")
                    y = False
                    return True


if __name__ == "__main__":
    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (Delete the "#" and space before each line.)
    # IMPORTANT: keep this code indented inside the "if __name__ == '__main__'" block
    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'disable': ['R1705', 'E9998', 'E9999', 'static_type_checker']
    # })

    DORM = 1  # initial starting location
    MAX_MOVE = 20
    undo_chances = 3

    game_log = EventList()  # This is REQUIRED as one of the baseline requirements
    game = AdventureGame('game_data.json', DORM)  # load data, setting initial location ID to 1
    menu = ["look", "inventory", "score", "log", "quit", "undo"]  # Regular menu options available at each location
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
            print(f"LOCATION {location.id_num}      (Moves {game.moves})\n{location.brief_description}")
        else:
            print(f"LOCATION {location.id_num}      (Moves {game.moves})\n{location.long_description}")
            location.visited = True

        # Display possible actions at this location
        print("What to do? Choose from: look, inventory, score, log, quit, undo")
        print("At this location, you can also:")
        for action in location.available_commands:
            print("-", action)

        # Display possible take at this location
        for item_name in location.items:
            itm = game.get_item(item_name)
            if not itm.deposited:
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
                    print("-", item.name)
            elif choice == "score":
                print("Current score:", game.score)
            elif choice == "undo":
                if game.moves >= 1 and undo_chances > 0:
                    if game.undo_action(game_log):
                        undo_chances -= 1
                        print("You have undone your move.", undo_chances, " more remaining undo chances.")
                    else:
                        print("Cannot undo. Previous command is from menu")
                elif undo_chances == 0:
                    print("Cannot undo. You have run out of undo chances.")
                    print("Complete the puzzle at the Bahen for more undo chances.")
                else:
                    print("Cannot undo. You have not made any move yet.")
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
                item_name = choice[5:]

                if location.puzzle_words:
                    print("You must complete the puzzle to obtain the item.")
                    print("Guess the word related to the location you're in, one letter at a time. You have 10 tries.")
                    if game.puzzle(location):
                        if game.take_item(location.id_num, item_name):
                            game.moves += 1
                    else:
                        print("Cannot take item because puzzle failed")

            elif choice.startswith("deposit "):
                item_name = choice[8:]
                if game.deposit_item(location.id_num, item_name):
                    game.moves += 1

                # check if this location is the dorm and all 3 item are present (Win conditon)
                if location.id_num == DORM and all(
                        itm in location.items for itm in ["laptop charger", "lucky mug", "usb drive"]):
                    print("YOU WIN!!!")
                    print("With all your items recovered," +
                          " you rush back to your dorm and submit the project just in time.")
                    print(f"Final Score: {game.score}")
                    print(f"moves taken: {game.moves}")
                    game.ongoing = False

        if game.moves == MAX_MOVE:  # Runs out of moves (Game Over)
            game.ongoing = False
            print("GAME OVER")
            print("Time's up — the deadline has passed, and the project was not submitted.")
            print(f"Final Score: {game.score}")
            print(f"moves taken: {game.moves}")
