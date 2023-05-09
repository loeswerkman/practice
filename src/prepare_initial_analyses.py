"""
This file will prepare a summary of the EN-ES Miami dataset that can be used to then perform
 the exploratory analyses on in a second Jupyter Notebook file.

The summary (summaryPerPersonPerConversation.txt) will contain:
    1) Total word count per speaker per conversation
    2) TODO: Word count English words
    3) TODO: Word count Spanish words
    4) Counts of 'um' in the conversations
    5) Counts of fillers 'yeah', 'like', 'pues', and 'eso' TODO: Calculations currently take not only fillers but ALL
"""
# -
# IMPORTS
import re
import urllib.request as urllib2
from typing import List, Iterable, Dict, Set, TextIO, Tuple
from string import ascii_letters


# -
# ABSOLUTES
import nltk

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
class WordCountSummary:
    def __init__(self, word_count: int, word_count_english: int, word_count_spanish: int, um_count: int,
                 uh_count: int, em_count: int, eh_count: int, am_count: int, ah_count: int):
        self.word_count = word_count
        self.word_count_english = word_count_english
        self.word_count_spanish = word_count_spanish
        self.um_count = um_count
        self.uh_count = uh_count
        self.em_count = em_count
        self.eh_count = eh_count
        self.am_count = am_count
        self.ah_count = ah_count


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
        + '|\[- (spa|eng)]|[()]|\[\?]|\+,|\[(= ?!|\*) .+]|_|\+[+^]|<|>|\+|:)',  # FixMe: Clean up regex
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


def get_line_summary(line: str) -> WordCountSummary:
    spoken_line = remove_non_spoken_parts(line)

    unknown_text_parts = set(spoken_line).difference(ascii_letters + "ÁáÉéÍíÓóÚúüÑñ '-")
    spoken_line.split()
    if unknown_text_parts:
        raise UnknownTextPartError(line, unknown_text_parts)

    return get_all_line_counts(spoken_line)


def get_all_line_counts(line: str) -> WordCountSummary:
    spanish_word_count, english_word_count = (0, 0)
    um_count, uh_count, em_count, eh_count, am_count, ah_count = (0, 0, 0, 0, 0, 0)

    words = line.split()
    for i, word in enumerate(words):
        word = word.lower()
        match word:
            case 'um': um_count += 1
            case 'uh': uh_count += 1
            case 'em': em_count += 1
            case 'uh': eh_count += 1
            case 'am':
                if nltk.pos_tag(nltk.word_tokenize(line), tagset="universal")[i][1] != 'VERB':
                    # We are making sure that the 'am' we are finding is not used as a verb
                    #  like in the sentence 'I am 22 years old'.
                    # The pos_tag function returns a list where each word is represented by a
                    #  tuple of which the first item is the word and the second the POS tag.
                    # We are checking to ensure that the POS tag of our word is not a verb to
                    #  filter out the 'am's with meaning such as in the sentence 'I am Loes'.
                    am_count += 1
            case 'ah': ah_count += 1
        # TODO: Insert logic to calculate nr of English and Spanish words

    return WordCountSummary(
        word_count=len(words),
        word_count_english=english_word_count,
        word_count_spanish=spanish_word_count,
        um_count=um_count,
        uh_count=uh_count,
        em_count=em_count,
        eh_count=eh_count,
        am_count=am_count,
        ah_count=ah_count
    )


def process_file(file_name: str, progress_file: TextIO):
    word_counts_per_speaker: Dict[str, WordCountSummary] = {}

    for line in urllib2.urlopen('http://siarad.org.uk/chats/miami/' + file_name):
        line = line.decode('utf-8').rstrip()  # Removes the "b''" in "b'<line>'" and the "/n"
        if not is_part_of_conversation(line):
            continue

        line_summary = get_line_summary(line)
        speaker = get_speaker(line)

        if speaker not in word_counts_per_speaker.keys():
            word_counts_per_speaker[speaker] = WordCountSummary(
                 word_count=line_summary.word_count,
                 word_count_english=line_summary.word_count_english,
                 word_count_spanish=line_summary.word_count_spanish,
                 um_count=line_summary.um_count,
                 uh_count=line_summary.uh_count,
                 em_count=line_summary.em_count,
                 eh_count=line_summary.eh_count,
                 am_count=line_summary.am_count,
                 ah_count=line_summary.ah_count
            )
        else:
            word_counts_per_speaker[speaker].word_count += line_summary.word_count
            word_counts_per_speaker[speaker].word_count_english += line_summary.word_count_english
            word_counts_per_speaker[speaker].word_count_spanish += line_summary.word_count_spanish
            word_counts_per_speaker[speaker].um_count += line_summary.um_count
            word_counts_per_speaker[speaker].uh_count += line_summary.uh_count
            word_counts_per_speaker[speaker].em_count += line_summary.em_count
            word_counts_per_speaker[speaker].eh_count += line_summary.eh_count
            word_counts_per_speaker[speaker].am_count += line_summary.am_count
            word_counts_per_speaker[speaker].ah_count += line_summary.ah_count

    # All lines were processed.
    write_summary_file(file_name, progress_file, word_counts_per_speaker)


def write_summary_file(file_name, progress_file, word_counts_per_speaker):
    for speaker in word_counts_per_speaker.keys():
        progress_file.write(
            speaker + '\t'
            + file_name + '\t'
            + str(word_counts_per_speaker[speaker].word_count) + '\t'
            + str(word_counts_per_speaker[speaker].word_count_english) + '\t'
            + str(word_counts_per_speaker[speaker].word_count_spanish) + '\t'
            + str(word_counts_per_speaker[speaker].um_count) + '\t'
            + str(word_counts_per_speaker[speaker].uh_count) + '\t'
            + str(word_counts_per_speaker[speaker].em_count) + '\t'
            + str(word_counts_per_speaker[speaker].eh_count) + '\t'
            + str(word_counts_per_speaker[speaker].am_count) + '\t'
            + str(word_counts_per_speaker[speaker].ah_count) + '\n'
        )


# -
# -
# -
# MAIN
if __name__ == "__main__":
    with open('../output/summaryPerPersonPerConversation.txt', 'w') as summary_file:
        summary_file.write(
            'speaker\tconversation\ttotal\tenglish\tspanish\tum\tuh\tem\teh\tam\tah\n'
        )  # Header line

        try:
            for file_name in get_filenames():
                print(file_name)
                process_file(file_name, summary_file)

        except UnknownTextPartError as unknown_text_part_error:
            # This except will be used to show us information on sentences that contain signs or
            #  anything that we have yet to find a way to deal with. We print the sentence in
            #  question, so we can easily see the characters that we don't understand yet, and
            #  can then add the necessary logic to the code and restart the code.
            exit(
                'Error: Find a way to handle the ' + str(unknown_text_part_error.unknown_text_parts)
                + ' symbol(s) as found in the following line:\n'
                + unknown_text_part_error.line
            )
