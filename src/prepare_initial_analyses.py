"""
This file will prepare two summaries of the EN-ES Miami dataset that can be used to then perform
 the exploratory analyses on in a second Jupyter Notebook file.

The first summary (summaryPerConversation.txt) will contain:
    1) Total word count per conversation
    2) TODO: Word count English words
    3) TODO: Word count Spanish words
    4) Counts of 'um' in the conversations
    5) Counts of fillers 'yeah', 'like', 'pues', and 'eso' TODO: Calculations currently take not only fillers but ALL

The second summary (summaryPerPerson.txt) will contain:
    1) Total word count per person
    2) TODO: Total English word count per person
    3) TODO: Total Spanish word count per person
    4) Counts of 'um' per person
    5) Counts of fillers 'yeah', 'like', 'pues', and 'eso' TODO: Calculations currently take not only fillers but ALL
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
class WordCountSummary:
    def __init__(self, word_count: int, word_count_english: int, word_count_spanish: int, um_count: int,
                 yeah_count: int, like_count: int, pues_count: int, eso_count: int):
        self.word_count = word_count
        self.word_count_english = word_count_english
        self.word_count_spanish = word_count_spanish
        self.um_count = um_count
        self.yeah_count = yeah_count
        self.like_count = like_count
        self.pues_count = pues_count
        self.eso_count = eso_count


class UnknownTextPartError(Exception):
    def __init__(self, line: str, unknown_text_parts: Set[str]):
        self.line = line
        self.unknown_text_parts = unknown_text_parts


# -
# -
# -
# SUPER UGLY SOLUTION USING A SORT OF SUPERGLOBAL FixMe: Make prettier please!
word_counts_per_speaker: Dict[str, WordCountSummary] = {}


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
    um_count, spanish_word_count, english_word_count = (0, 0, 0)
    yeah_count, like_count, pues_count, eso_count = (0, 0, 0, 0)
    words = line.split()
    for word in words:
        word = word.lower()
        if word == 'um' or word == 'uh' or word == 'er':
            um_count += 1
        if word == 'yeah':
            yeah_count += 1
        if word == 'like':
            like_count += 1
        if word == 'pues':
            pues_count += 1
        if word == 'eso':
            eso_count += 1
        # TODO: Insert logic to calculate nr of English and Spanish words

    return WordCountSummary(
        word_count=len(words),
        word_count_english=english_word_count,
        word_count_spanish=spanish_word_count,
        um_count=um_count,
        yeah_count=yeah_count,
        like_count=like_count,
        pues_count=pues_count,
        eso_count=eso_count,
    )


def process_new_speaker_counts(speaker: str, line_summary: WordCountSummary):
    global word_counts_per_speaker

    if speaker not in word_counts_per_speaker.keys():
        word_counts_per_speaker[speaker] = WordCountSummary(
            word_count=line_summary.word_count,
            word_count_english=line_summary.word_count_english,
            word_count_spanish=line_summary.word_count_spanish,
            um_count=line_summary.um_count,
            yeah_count=line_summary.yeah_count,
            like_count=line_summary.like_count,
            pues_count=line_summary.pues_count,
            eso_count=line_summary.eso_count,
        )
    else:
        word_counts_per_speaker[speaker].word_count += line_summary.word_count
        word_counts_per_speaker[speaker].word_count_english += line_summary.word_count_english
        word_counts_per_speaker[speaker].word_count_spanish += line_summary.word_count_spanish
        word_counts_per_speaker[speaker].um_count += line_summary.um_count
        word_counts_per_speaker[speaker].yeah_count += line_summary.yeah_count
        word_counts_per_speaker[speaker].like_count += line_summary.like_count
        word_counts_per_speaker[speaker].pues_count += line_summary.pues_count
        word_counts_per_speaker[speaker].eso_count += line_summary.eso_count


def process_file(file_name: str, progress_file: TextIO):
    convo_um_count, convo_word_count, convo_spanish_word_count, convo_english_word_count = (0, 0, 0, 0)
    convo_yeah_count, convo_like_count, convo_pues_count, convo_eso_count = (0, 0, 0, 0)

    for line in urllib2.urlopen('http://siarad.org.uk/chats/miami/' + file_name):
        line = line.decode('utf-8').rstrip()  # Removes the "b''" in "b'<line>'" and the "/n"
        if not is_part_of_conversation(line):
            continue

        line_summary = get_line_summary(line)
        speaker = get_speaker(line)
        process_new_speaker_counts(speaker, line_summary)

        convo_word_count += line_summary.word_count
        convo_spanish_word_count += line_summary.word_count_spanish
        convo_english_word_count += line_summary.word_count_english
        convo_um_count += line_summary.um_count
        convo_yeah_count += line_summary.yeah_count
        convo_like_count += line_summary.like_count
        convo_pues_count += line_summary.pues_count
        convo_eso_count += line_summary.eso_count

    # All lines were processed.
    progress_file.write(
        file_name + '\t'
        + str(convo_word_count) + '\t'
        + str(convo_english_word_count) + '\t'
        + str(convo_spanish_word_count) + '\t'
        + str(convo_um_count) + '\t'
        + str(convo_yeah_count) + '\t'
        + str(convo_like_count) + '\t'
        + str(convo_pues_count) + '\t'
        + str(convo_eso_count) + '\n'
    )


# -
# -
# -
# MAIN
if __name__ == "__main__":
    columns = 'total\tenglish\tspanish\tum\tyeah\tlike\tpues\teso'
    with open('../output/summaryPerConversation.txt', 'w') as summary_per_conversation_file:
        summary_per_conversation_file.write('conversation\t' + columns + '\n')  # Header line

        try:
            for file_name in get_filenames():
                print(file_name)
                process_file(file_name, summary_per_conversation_file)

        except UnknownTextPartError as unknown_text_part_error:
            # This except will be used to show us information on sentences that contain signs or
            #  anything that we have yet to find a way to deal with. We print the sentence in
            #  question, so we can easily see the characters that we don't understand yet, and
            #  can then add the necessary logic to the code and restart the code.
            exit(
                'Error in file ' + file_name + ':\n'
                + 'Find a way to handle the ' + str(unknown_text_part_error.unknown_text_parts)
                + ' symbol(s) as found in the following line:\n'
                + unknown_text_part_error.line
            )

    with open('../output/summaryPerPerson.txt', 'w') as summary_per_person_file:
        summary_per_person_file.write('name\t' + columns + '\n')  # Header line

        for speaker in word_counts_per_speaker.keys():
            print(speaker)
            summary_per_person_file.write(
                speaker + '\t'
                + str(word_counts_per_speaker[speaker].word_count) + '\t'
                + str(word_counts_per_speaker[speaker].word_count_english) + '\t'
                + str(word_counts_per_speaker[speaker].word_count_spanish) + '\t'
                + str(word_counts_per_speaker[speaker].um_count) + '\t'
                + str(word_counts_per_speaker[speaker].yeah_count) + '\t'
                + str(word_counts_per_speaker[speaker].like_count) + '\t'
                + str(word_counts_per_speaker[speaker].pues_count) + '\t'
                + str(word_counts_per_speaker[speaker].eso_count) + '\n'
            )
