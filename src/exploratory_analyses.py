""""
This file will contain the first exploratory analyses as done on the EN-ES spoken dataset.
It will contain:

    1) Word count English words
    2) Word count Spanish words
    3) Counts of 'um' in the conversations
    4) Use of 'um' compared to total word count
    5) These ratios per person
"""
# -
# IMPORTS
import re
from typing import List


# -
# -
# -
# DEFINE CLASSES
class Person:
    def __init__(self, name: str, age: int, sex: str, native_english: bool, native_spanish: bool):
        self.name = name
        self.sex = sex
        self.age = age
        self.native_english = native_english
        self.native_spanish = native_spanish


class ConversationSummary:
    def __init__(self, word_count: int, word_count_english: int, word_count_spanish: int,
                 um_count: int, persons: List[Person]):
        self.word_count = word_count
        self.word_count_english = word_count_english
        self.word_count_spanish = word_count_spanish
        self.um_count = um_count
        self.persons = persons


class UnknownTextPartError(Exception):
    pass


# -
# -
# -
# DEFINE FUNCTIONS
def is_part_of_conversation(line: str) -> bool:
    # In the .cha files we see that the actual conversational lines
    #  are identified by starting with an asterix.
    return line[0] == '*'


def remove_non_spoken_parts(line: str) -> str:
    return re.sub(
        '(\*[A-Z]{3}:\t|.*|<[^<]*>|\[/+]|\(\.+\))',
        # Examples of what will be removed:
        # 1) '*LAU:   '          -> Identifying a speaker
        # 2) '28938_31313' -> Information on timing
        # 3) '<she is>'          -> ?
        # 4) '[//]'              -> Representing a pause
        # 5) '(.)'               -> ?
        '',
        line
    )


def get_speaker(line: str) -> str:
    # This returns the part of the line that holds information on
    #  the speaker, e.g. 'LAU'.
    return line[1:4]


# -
# -
# -
# MAIN
if __name__ == "__main__":
    with open('../data/herring1.cha', 'r') as file:
        last_speaker = ''

        for line in file:
            try:
                if not is_part_of_conversation(line):
                    continue

                speaker = get_speaker(line)
                spoken_line = remove_non_spoken_parts(line)
                # LOES check for symbols that you don't know and if you find them, throw an
                #  UnknownTextPart error

            except UnknownTextPartError:
                print()
