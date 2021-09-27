from difflib import SequenceMatcher
import numpy as np

from math import floor, ceil


# Function to calculate the
# Jaro Similarity of two s
def jaro_distance(s1, s2):
    # If the s are equal
    if (s1 == s2):
        return 1.0

    # Length of two s
    len1 = len(s1)
    len2 = len(s2)

    # Maximum distance upto which matching
    # is allowed
    max_dist = floor(max(len1, len2) / 2) - 1

    # Count of matches
    match = 0

    # Hash for matches
    hash_s1 = [0] * len(s1)
    hash_s2 = [0] * len(s2)

    # Traverse through the first
    for i in range(len1):

        # Check if there is any matches
        for j in range(max(0, i - max_dist),
                       min(len2, i + max_dist + 1)):

            # If there is a match
            if (s1[i] == s2[j] and hash_s2[j] == 0):
                hash_s1[i] = 1
                hash_s2[j] = 1
                match += 1
                break

    # If there is no match
    if (match == 0):
        return 0.0

    # Number of transpositions
    t = 0
    point = 0

    # Count number of occurrences
    # where two characters match but
    # there is a third matched character
    # in between the indices
    for i in range(len1):
        if (hash_s1[i]):

            # Find the next matched character
            # in second
            while (hash_s2[point] == 0):
                point += 1

            if (s1[i] != s2[point]):
                point += 1
                t += 1
    t = t // 2

    # Return the Jaro Similarity
    return (match / len1 + match / len2 +
            (match - t + 1) / match) / 3.0


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def levenshtein_distance(ref, hyp):
    """Levenshtein distance is a string metric for measuring the difference
    between two sequences. Informally, the levenshtein disctance is defined as
    the minimum number of single-character edits (substitutions, insertions or
    deletions) required to change one word into the other. We can naturally
    extend the edits to word level when calculate levenshtein disctance for
    two sentences.
    """
    m = len(ref)
    n = len(hyp)

    # special case
    if ref == hyp:
        return 0
    if m == 0:
        return n
    if n == 0:
        return m

    if m < n:
        ref, hyp = hyp, ref
        m, n = n, m

    # use O(min(m, n)) space
    distance = np.zeros((2, n + 1), dtype=np.int32)

    # initialize distance matrix
    for j in range(0, n + 1):
        distance[0][j] = j

    # calculate levenshtein distance
    for i in range(1, m + 1):
        prev_row_idx = (i - 1) % 2
        cur_row_idx = i % 2
        distance[cur_row_idx][0] = i
        for j in range(1, n + 1):
            if ref[i - 1] == hyp[j - 1]:
                distance[cur_row_idx][j] = distance[prev_row_idx][j - 1]
            else:
                s_num = distance[prev_row_idx][j - 1] + 1
                i_num = distance[cur_row_idx][j - 1] + 1
                d_num = distance[prev_row_idx][j] + 1
                distance[cur_row_idx][j] = min(s_num, i_num, d_num)

    return distance[m % 2][n]


def vergleich(string1, string2):
    #print(string1, string2)
    #print(similar(string1, string2), "| Similar")  # would have a high prob.
    #print(levenshtein_distance(string1, string2), "| Levenshtein Distance")  # would have a high prob.
    #print(jaro_distance(string1, string2), "| Jaro Distance")  # would have a high prob.

    return similar(string1, string2), jaro_distance(string1, string2), levenshtein_distance(string1, string2), (len(string1) + len(string2)) / 2

r'''
vergleich("ʊnt ˈkøːnɪç", "ˈʊnkɛːnɪç")
print()
vergleich("ʊnt ˈkøːnɪç", "ˈʊnk ɛːnɪç")
print()
vergleich("ʊnt ˈkøːnɪç", "ˈʊn kɛːnɪç")

print()
vergleich("ʊnt ˈkøːnɪç", "ˈʊ nkɛːnɪç")
print()
vergleich("ʊnt ˈkøːnɪç", "ˈʊnkɛ ːnɪç")


vergleich("ˈhɛʁʦoːgɪn ʊnt ˈkøːnɪç fɛɐ̯ˈʔaɪ̯nbaːɐ̯tən dɔʁt diː ˈhalpʦaɪ̯t ˈiːʀɐ ˈbaɪ̯dən ˈkɪndɐ", "ˈhɛʁʦoːgɪn ʊnt ˈkøːnɪç fɛɐ̯ˈʔaɪ̯nbaːɐ̯tən dɔʁt diː ˈhoːχʦaɪ̯t ˈiːʀɐ ˈbaɪ̯dən ˈkɪndɐ")'''


# Irgendwie so programmieren, dass die Wörter genauso wie der Targetsatz gesplittet sind. Das durch die die Distanz
# Berechnung machen, schauen wo das Leerzeichen am besten platziert ist. Also erst weg machen dann hin, sofern nicht schon gut
# Dann sieht man, welche Wörter wie gut aufeinander passen und dadurch den Sprachfehler erkennen.





# Squencematcher: Gut

# Hamming distance: Berücksichtigt nicht überflüssige Characters, daher nicht brauchbar

# Levenshtein distance: Gut, misst die gesamten unterschiedlichen Fehler

# Damerau Levenshtein: hat Probleme mit den Sonderzeichen, daher unbrauchbar.

# Jaro Distance ist auch besser, um auszuwählen, welches der beiden Möglichen Aussprachen (Homographe) man nehmen sollte