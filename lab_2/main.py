"""
Longest common subsequence problem
"""
import tokenizer


def tokenize_by_lines(text: str) -> tuple:
    """
    Splits a text into sentences, sentences – into tokens,
    converts the tokens into lowercase, removes punctuation
    :param text: the initial text
    :return: a list of sentences with lowercase tokens without punctuation
    e.g. text = 'I have a cat.\nHis name is Bruno'
    --> (('i', 'have', 'a', 'cat'), ('his', 'name', 'is', 'bruno'))
    """
    if not isinstance(text, str):
        return ()
    text = text.split('.')
    sentences_list = []
    for sentence in text:
        sentence = tokenizer.tokenize(sentence)
        if sentence:
            sentences_list.append(tuple(sentence))
    tokenized_text = tuple(sentences_list)
    return tokenized_text


def create_zero_matrix(rows: int, columns: int) -> list:
    """
    Creates a matrix rows * columns where each element is zero
    :param rows: a number of rows
    :param columns: a number of columns
    :return: a matrix with 0s
    e.g. rows = 2, columns = 2
    --> [[0, 0], [0, 0]]
    """
    if not isinstance(rows, int) or not isinstance(columns, int):
        return []
    if isinstance(rows, bool) or isinstance(columns, bool):
        return []
    if rows < 1 or columns < 1:
        return []
    matrix = [[0] * columns for _ in range(rows)]
    return matrix


def fill_lcs_matrix(first_sentence_tokens: tuple, second_sentence_tokens: tuple) -> list:
    """
    Fills a longest common subsequence matrix using the Needleman–Wunsch algorithm
    :param first_sentence_tokens: a tuple of tokens
    :param second_sentence_tokens: a tuple of tokens
    :return: a lcs matrix
    """
    if not isinstance(first_sentence_tokens, tuple) or not isinstance(second_sentence_tokens, tuple):
        return []

    if (not first_sentence_tokens
            or not second_sentence_tokens or
            not all(isinstance(el, str) for el in first_sentence_tokens + second_sentence_tokens)):
        return []

    lcs = create_zero_matrix(len(first_sentence_tokens), len(second_sentence_tokens))

    for i, i_word in enumerate(first_sentence_tokens):
        for j, j_word in enumerate(second_sentence_tokens):
            if i_word == j_word:
                lcs[i][j] = lcs[i - 1][j - 1] + 1
            else:
                lcs[i][j] = max(lcs[i][j - 1], lcs[i - 1][j])
    return lcs


def find_lcs_length(first_sentence_tokens: tuple, second_sentence_tokens: tuple, plagiarism_threshold: float) -> int:
    """
    Finds a length of the longest common subsequence using the Needleman–Wunsch algorithm
    When a length is less than the threshold, it becomes 0
    :param first_sentence_tokens: a tuple of tokens
    :param second_sentence_tokens: a tuple of tokens
    :param plagiarism_threshold: a threshold
    :return: a length of the longest common subsequence
    """
    if (not isinstance(first_sentence_tokens, tuple) or
            not isinstance(second_sentence_tokens, tuple) or
            not isinstance(plagiarism_threshold, float) or
            isinstance(plagiarism_threshold, bool) or
            plagiarism_threshold > 1 or
            plagiarism_threshold < 0):
        return -1
    if len(first_sentence_tokens) > len(second_sentence_tokens):
        first_sentence_tokens, second_sentence_tokens = second_sentence_tokens, first_sentence_tokens
    lcs = fill_lcs_matrix(first_sentence_tokens, second_sentence_tokens)
    if not lcs:
        if first_sentence_tokens == () or second_sentence_tokens == ():
            return 0
        return -1
    lcs_length = lcs[-1][-1]
    if lcs_length / len(second_sentence_tokens) >= plagiarism_threshold:
        return lcs_length
    return 0


def find_lcs(first_sentence_tokens: tuple, second_sentence_tokens: tuple, lcs_matrix: list) -> tuple:
    """
    Finds the longest common subsequence itself using the Needleman–Wunsch algorithm
    :param first_sentence_tokens: a tuple of tokens
    :param second_sentence_tokens: a tuple of tokens
    :param lcs_matrix: a filled lcs matrix
    :return: the longest common subsequence
    """
    if (not isinstance(first_sentence_tokens, tuple) or
            not isinstance(second_sentence_tokens, tuple) or
            not isinstance(lcs_matrix, list) or
            not lcs_matrix or
            not first_sentence_tokens or
            not second_sentence_tokens or
            not all(isinstance(el, str) for el in first_sentence_tokens + second_sentence_tokens) or
            not all(isinstance(el, list) for el in lcs_matrix) or
            not isinstance(lcs_matrix[0][0], int) or
            not lcs_matrix[-1][-1]):
        return ()

    if len(first_sentence_tokens) > len(second_sentence_tokens):
        first_sentence_tokens, second_sentence_tokens = second_sentence_tokens, first_sentence_tokens

    i = len(first_sentence_tokens) - 1
    j = len(second_sentence_tokens) - 1
    lcs = []

    while i >= 0 and j >= 0:
        if first_sentence_tokens[i] == second_sentence_tokens[j]:
            lcs.append(second_sentence_tokens[i])
            i -= 1
            j -= 1
        elif lcs_matrix[i - 1][j] > lcs_matrix[i][j - 1]:
            i -= 1
        else:
            j -= 1

    if lcs_matrix[0][0] == 1:
        lcs.append(first_sentence_tokens[0])

    lcs = tuple(lcs[::-1])
    return lcs


def calculate_plagiarism_score(lcs_length: int, suspicious_sentence_tokens: tuple) -> float:
    """
    Calculates the plagiarism score
    The score is the lcs length divided by the number of tokens in a suspicious sentence
    :param lcs_length: a length of the longest common subsequence
    :param suspicious_sentence_tokens: a tuple of tokens
    :return: a score from 0 to 1, where 0 means no plagiarism, 1 – the texts are the same
    """
    if (not isinstance(lcs_length, int) or
            not isinstance(suspicious_sentence_tokens, tuple) or
            not all(isinstance(el, str) for el in suspicious_sentence_tokens)):
        return -1.0
    if not suspicious_sentence_tokens:
        return 0.0
    if (lcs_length > len(suspicious_sentence_tokens) or
            lcs_length < 0 or
            isinstance(lcs_length, bool)):
        return -1.0

    plagiarism_score = lcs_length / len(suspicious_sentence_tokens)
    return plagiarism_score


def filler(original_text_tokens, suspicious_text_tokens):
    length_diff = len(original_text_tokens) - len(suspicious_text_tokens)
    original_text_tokens = list(original_text_tokens)
    for i in range(-length_diff):
        original_text_tokens.append(())
    orig_text_tokens = tuple(original_text_tokens)
    return orig_text_tokens


def calculate_text_plagiarism_score(original_text_tokens: tuple, suspicious_text_tokens: tuple,
                                    plagiarism_threshold=0.3) -> float:
    """
    Calculates the plagiarism score: compares two texts line by line using lcs
    The score is the sum of lcs values for each pair divided by the number of tokens in suspicious text
    At the same time, a value of lcs is compared with a threshold (e.g. 0.3)
    :param original_text_tokens: a tuple of sentences with tokens
    :param suspicious_text_tokens: a tuple of sentences with tokens
    :param plagiarism_threshold: a threshold
    :return: a score from 0 to 1, where 0 means no plagiarism, 1 – the texts are the same
    """
    if (not isinstance(original_text_tokens, tuple) or
            not isinstance(suspicious_text_tokens, tuple) or
            not all(isinstance(el, tuple) for el in original_text_tokens + suspicious_text_tokens) or
            not all(isinstance(el, str) for el in original_text_tokens[0] + suspicious_text_tokens[0])):
        return -1.0

    if len(original_text_tokens) < len(suspicious_text_tokens):
        original_text_tokens = filler(original_text_tokens, suspicious_text_tokens)

    plagiarism = 0

    for i, s_sent in enumerate(suspicious_text_tokens):
        lcs_length = find_lcs_length(s_sent, original_text_tokens[i], plagiarism_threshold)
        plagiarism_score = calculate_plagiarism_score(lcs_length, s_sent)
        plagiarism += plagiarism_score

    plagiarism = plagiarism / len(suspicious_text_tokens)

    return plagiarism


def find_diff_in_sentence(original_sentence_tokens: tuple, suspicious_sentence_tokens: tuple, lcs: tuple) -> tuple:
    """
    Finds words not present in lcs.
    :param original_sentence_tokens: a tuple of tokens
    :param suspicious_sentence_tokens: a tuple of tokens
    :param lcs: a longest common subsequence
    :return: a tuple with tuples of indexes
    """
    if (not isinstance(original_sentence_tokens, tuple) or
            not isinstance(suspicious_sentence_tokens, tuple) or
            not isinstance(lcs, tuple) or
            not all(isinstance(el, str) for el in original_sentence_tokens + suspicious_sentence_tokens + lcs)):
        return ()

    sentences = (original_sentence_tokens, suspicious_sentence_tokens)
    diff = []

    for sent in sentences:
        diff_sub = []
        for i, word in enumerate(sent):
            if word not in lcs:
                if i == 0 or sent[i - 1] in lcs:
                    diff_sub.append(i)
                if i == len(sent) - 1 or sent[i + 1] in lcs:
                    diff_sub.append(i + 1)
        diff.append(tuple(diff_sub))

    diff = tuple(diff)
    return diff


def accumulate_diff_stats(original_text_tokens: tuple, suspicious_text_tokens: tuple, plagiarism_threshold=0.3) -> dict:
    """
    Accumulates the main statistics for pairs of sentences in texts:
            lcs_length, plagiarism_score and indexes of differences
    :param original_text_tokens: a tuple of sentences with tokens
    :param suspicious_text_tokens: a tuple of sentences with tokens
    :return: a dictionary of main statistics for each pair of sentences
    including average text plagiarism, sentence plagiarism for each sentence and lcs lengths for each sentence
    {'text_plagiarism': int,
     'sentence_plagiarism': list,
     'sentence_lcs_length': list,
     'difference_indexes': list}
    """
    if (not isinstance(original_text_tokens, tuple) or
            not isinstance(suspicious_text_tokens, tuple) or
            not all(isinstance(el, tuple) for el in original_text_tokens + suspicious_text_tokens) or
            not all(isinstance(el, str) for el in original_text_tokens[0] + suspicious_text_tokens[0])):
        return {}

    text_plagiarism = calculate_text_plagiarism_score(original_text_tokens, suspicious_text_tokens)

    stat = {'text_plagiarism': text_plagiarism,
            'sentence_plagiarism': [],
            'sentence_lcs_length': [],
            'difference_indexes': []}

    if len(original_text_tokens) < len(suspicious_text_tokens):
        original_text_tokens = filler(original_text_tokens, suspicious_text_tokens)

    for orig_sent, s_sent in zip(original_text_tokens, suspicious_text_tokens):
        lcs_length = find_lcs_length(orig_sent, s_sent, plagiarism_threshold)
        stat['sentence_lcs_length'].append(lcs_length)
        stat['sentence_plagiarism'].append(calculate_plagiarism_score(lcs_length, s_sent))
        lcs_matrix = fill_lcs_matrix(orig_sent, s_sent)
        lcs = find_lcs(orig_sent, s_sent, lcs_matrix)
        stat['difference_indexes'].append(find_diff_in_sentence(orig_sent, s_sent, lcs))

    return stat


def create_diff_report(original_text_tokens: tuple, suspicious_text_tokens: tuple, accumulated_diff_stats: dict) -> str:
    """
    Creates a diff report for two texts comparing them line by line
    :param original_text_tokens: a tuple of sentences with tokens
    :param suspicious_text_tokens: a tuple of sentences with tokens
    :param accumulated_diff_stats: a dictionary with statistics for each pair of sentences
    :return: a report
    """
    if (not isinstance(original_text_tokens, tuple) or
            not isinstance(suspicious_text_tokens, tuple) or
            not all(isinstance(el, tuple) for el in original_text_tokens + suspicious_text_tokens) or
            not all(isinstance(el, str) for el in original_text_tokens[0] + suspicious_text_tokens[0]) or
            not isinstance(accumulated_diff_stats, dict)):
        return ''

    if len(original_text_tokens) < len(suspicious_text_tokens):
        original_text_tokens = filler(original_text_tokens, suspicious_text_tokens)

    diff_report = ''
    number_of_sent = len(suspicious_text_tokens)

    for sent_ind in range(number_of_sent):
        orig_sent = list(original_text_tokens[sent_ind])
        s_sent = list(suspicious_text_tokens[sent_ind])
        difference_indexes = accumulated_diff_stats['difference_indexes'][sent_ind]

        change_ind = 0
        for index in difference_indexes[0]:
            orig_sent.insert(index + change_ind, '|')
            s_sent.insert(index + change_ind, '|')
            change_ind += 1

        orig_sent = ' '.join(orig_sent)
        s_sent = ' '.join(s_sent)

        sent_lcs_length = accumulated_diff_stats['sentence_lcs_length'][sent_ind]
        sent_plagiarism = float(accumulated_diff_stats['sentence_plagiarism'][sent_ind] * 100)

        diff_report += f"- {orig_sent}\n+ {s_sent}\n\nlcs = {sent_lcs_length}, plagiarism = {sent_plagiarism}%\n\n"

    text_plagiarism = accumulated_diff_stats['text_plagiarism'] * 100

    diff_report += f"Text average plagiarism (words): {text_plagiarism}%"

    return diff_report


def find_lcs_length_optimized(first_sentence_tokens: tuple, second_sentence_tokens: tuple,
                              plagiarism_threshold: float) -> int:
    """
    Finds a length of the longest common subsequence using an optimized algorithm
    When a length is less than the threshold, it becomes 0
    :param first_sentence_tokens: a tuple of tokens
    :param second_sentence_tokens: a tuple of tokens
    :param plagiarism_threshold: a threshold
    :return: a length of the longest common subsequence
    """
    return 0


def tokenize_big_file(path_to_file: str) -> tuple:
    """
    Reads, tokenizes and transforms a big file into a numeric form
    :param path_to_file: a path
    :return: a tuple with ids
    """
    return()
