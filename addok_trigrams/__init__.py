"Trigram based algorithm for Addok."
from addok.helpers.results import _match_housenumber


def housenumber_field_key(s):
    return 'h|{}'.format(s.raw)


def compute_trigrams(token):
    if token.isdigit():
        return [token]
    max = len(token)
    if max < 3:
        return [token]
    return [token[i:i+3] for i in range(0, max - 2)]

LADLEFUL = 10


def trigramize(pipe):
    position = 0
    for token in pipe:
        for trigram in compute_trigrams(token):
            yield token.update(trigram, position=position, raw=token)
            position += 1


def match_housenumber(helper, result):
    # Group by position.
    tokens = {t.raw.position: t.raw for t in helper.tokens}
    # Reorder by position.
    tokens = [v for k, v in sorted(tokens.items())]
    _match_housenumber(helper, result, tokens)


def extend_results_removing_numbers(helper):
    # Only if bucket is empty or we have margin on should_match_threshold.
    if helper.bucket_empty\
       or len(helper.meaningful) - 1 > helper.should_match_threshold:

        # Remove numbers
        helper.debug('Trying to remove numbers.')
        keys = [t.db_key for t in helper.meaningful if not t.isdigit()]
        helper.add_to_bucket(keys, limit=LADLEFUL)
        if helper.bucket_overflow:
            return True


def extend_results_removing_one_whole_word(helper):
    if helper.bucket_empty\
       or len(helper.meaningful) - 1 > helper.should_match_threshold:
        helper.debug('Trying to remove trigrams of a same word.')
        # Group by word, so we can remove one word all in a once.
        words = set([t.raw for t in helper.meaningful])
        if len(words) > 2:
            # Do not remove one entire word if we have only two, as doing
            # search with only one word often is too noisy.
            for word in words:
                helper.debug('Removing word %s', word)
                keys = [t.db_key for t in helper.meaningful if t.raw != word]
                helper.add_to_bucket(keys, limit=LADLEFUL)
                if helper.bucket_overflow:
                    return True


def extend_results_removing_successive_trigrams(helper):
    if helper.bucket_empty\
       or len(helper.meaningful) - 1 > helper.should_match_threshold:
        helper.debug('Trying to remove sucessive triplet of trigrams.')
        helper.meaningful.sort(key=lambda x: x.position)
        for i in range(len(helper.meaningful)):
            helper.debug('Removing trigrams %s.', helper.meaningful[i:i+3])
            keys = [t.db_key for t
                    in (helper.meaningful[:i] + helper.meaningful[i + 3:])]
            helper.add_to_bucket(keys, limit=LADLEFUL)
            if helper.bucket_overflow:
                return True


VERSION = (0, 1, 0)

__author__ = 'Yohan Boniface'
__contact__ = "yohan.boniface@data.gouv.fr"
__homepage__ = "https://github.com/addok/addok-trigrams"
__version__ = ".".join(map(str, VERSION))
