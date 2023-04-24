"""
This file will prepare two summaries of the EN-ES Miami dataset that can be used to then perform
 the exploratory analyses on in a second Jupyter Notebook file.

The first summary (summaryPerConversation.txt) will contain:
    1) Total word count per conversation
    2) TODO: Word count English words
    3) TODO: Word count Spanish words
    4) Counts of 'um' in the conversations
    5) TODO: Counts of 'yeah' and 'like' when used as fillers

TODO: The second summary (summaryPerPerson.txt) will contain:
    1) Total word count per person
    2) Total English word count per person
    3) Total Spanish word count per person
    4) Counts of 'um' per person
    5) Counts of 'yeah' and 'like' when used as fillers
"""
# -
# IMPORTS
import re
import urllib.request as urllib2
from typing import List, Iterable, Dict, Set, TextIO
from string import ascii_letters


# -
# ABSOLUTES
CONVERSATIONS: Dict[str, Iterable[int]] = {
    'herring': {i for i in range(1, 18) if i != 4},
    'maria': {1, 2, 4, 7, 10, 16, 18, 19, 20, 21, 24, 27, 30, 31, 40},
    'sastre': range(1, 14),
    'zeledon': {1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 13, 14}
}


# -
# -
# -
# DEFINE CLASSES
# class Person:
#     def __init__(self, name: str, age: int, sex: str, native_english: bool, native_spanish: bool):
#         self.name = name
#         self.sex = sex
#         self.age = age
#         self.native_english = native_english
#         self.native_spanish = native_spanish TODO: Add this in


class LineSummary:
    def __init__(self, word_count: int, word_count_english: int,
                 word_count_spanish: int, um_count: int):
        # self.speaker = speaker TODO: Add this in
        self.word_count = word_count
        self.word_count_english = word_count_english
        self.word_count_spanish = word_count_spanish
        self.um_count = um_count


# class ConversationSummary:
#     def __init__(self, file_name: str, word_count: int, word_count_english: int,
#                  word_count_spanish: int, um_count: int):
#         self.file_name = file_name
#         self.word_count = word_count
#         self.word_count_english = word_count_english
#         self.word_count_spanish = word_count_spanish
#         self.um_count = um_count
        # self.persons = persons TODO: Add this in


class UnknownTextPartError(Exception):
    def __init__(self, line: str, unknown_text_parts: Set[str]):
        self.line = line
        self.unknown_text_parts = unknown_text_parts


# -
# -
# -
# DEFINE FUNCTIONS
def get_filenames() -> Iterable[str]:
    for name in CONVERSATIONS.keys():
        for number in CONVERSATIONS[name]:
            yield name + str(number) + '.cha'


def is_part_of_conversation(line: str) -> bool:
    # In the .cha files we see that the actual conversational lines
    #  are identified by starting with an asterisk.
    return line[0] == '*'


def remove_non_spoken_parts(line: str) -> str:
    return re.sub(
        '(\*[A-Z]{3}:\t|.*|<[^<]*>|\[(x [0-9]+|[/"!*-]+)]|\(\.+\)|:?@s:(eng|eng&spa|spa|ita|fra)(\+(eng|spa))?'
        + '|[.,?!]|\+<|\+\.\.[.?]|\+/+|\+"/|\+"|&=?[^ ]+'
        + '|\[- (spa|eng)]|[()]|\[\?]|\+,|\[(= ?!|\*) .+]|_|\+[+^]|<|>|\+|:)',
        # Examples of what will be removed:
        # 1) '*LAU:   '          -> Identifying a speaker
        # 2) '28938_31313' -> Information on timing
        # 3) '<she is>'          -> ?
        # 4) '[//]'              -> Representing a pause
        # 5) '(.)'               -> ?
        # 6) '@s:eng&spa+eng'    -> There to identify code-switching, but this one
        #                            is more often wrong than not, so we remove it
        # 7) '!?.,'               -> Ending a sentence or separating subsentences
        # 8) '+<'                -> ?
        # 9) '+...'              -> Representing a pause after finishing a sentence
        # 10) '+//'              -> ?
        # 11) '+"/'              -> ?
        # 12) '+"'               -> ?
        # 13a) '&=sigh'          -> Sounds that are not words
        # 13b) '&da'             -> A ton of options, all unclear what they mean but they do not show up in the audio
        # 14) '[- spa]'          -> Marker of code switching
        # 15) '(' or ')'         -> Brackets around autofilled part of text
        # 16) '[?]'              -> ?
        # 17) '[=! laughing]'    -> laughter
        # 18) '_'                -> ?
        # 19) '++' or '+^'       -> ?
        # 20) '<' or '>'         -> Any leftovers. Could mean anything.
        # 21) '+'                -> Any leftovers. Could mean anything.
        # 22) ':'                -> Any leftovers. Could mean anything.
        '',
        line
    )


def get_speaker(line: str) -> str:
    # This returns the part of the line that holds information on
    #  the speaker, e.g. 'LAU'.
    return line[1:4]


def get_line_summary(line: str) -> LineSummary:
    spoken_line = remove_non_spoken_parts(line)

    unknown_text_parts = set(spoken_line).difference(ascii_letters + "ÁáÉéÍíÓóÚúüÑñ '-")
    spoken_line.split()
    if unknown_text_parts:
        raise UnknownTextPartError(line, unknown_text_parts)

    return get_all_line_counts(spoken_line)


def get_all_line_counts(line: str) -> LineSummary:
    um_count, spanish_word_count, english_word_count = (0, 0, 0)

    words = line.split()
    for word in words:
        if word == 'um' or word == 'uh' or word == 'er':
            um_count += 1
        # TODO: Insert logic to calculate nr of English and Spanish words

    return LineSummary(
        word_count=len(words),
        word_count_english=english_word_count,
        word_count_spanish=spanish_word_count,
        um_count=um_count
    )


def process_file(file_name: str, progress_file: TextIO):
    um_count, word_count, spanish_word_count, english_word_count = (0, 0, 0, 0)
    for line in urllib2.urlopen('http://siarad.org.uk/chats/miami/' + file_name):
        line = line.decode('utf-8').rstrip()  # Removes the "b''" in "b'<line>'" and the "/n"
        if not is_part_of_conversation(line):
            continue

        line_summary = get_line_summary(line)

        um_count += line_summary.um_count
        word_count += line_summary.word_count
        spanish_word_count += line_summary.word_count_spanish
        english_word_count += line_summary.word_count_english

    # All lines were processed.
    progress_file.write(
        file_name + '\t'
        + str(word_count) + '\t'
        + str(english_word_count) + '\t'
        + str(spanish_word_count) + '\t'
        + str(um_count) + '\n'
    )


# -
# -
# -
# MAIN
if __name__ == "__main__":
    with open('../output/summaryPerConversation.txt', 'w') as summary_per_conversation_file:
        try:
            for file_name in get_filenames():
                print(file_name)
                process_file(file_name, summary_per_conversation_file)

        except UnknownTextPartError as unknown_text_part_error:
            # This except will be used to show us information on sentences that contain signs or
            #  anything that we have yet to find a way to deal with. We print the sentence in
            #  question, so we can easily see the characters that we don't understand yet, and
            #  can then add the necessary logic to the code and restart the code.
            print(
                'Error in file ' + file_name + ':\n'
                + 'Find a way to handle the ' + str(unknown_text_part_error.unknown_text_parts)
                + ' symbol(s) as found in the following line:\n'
                + unknown_text_part_error.line
            )
