import tokenize

try:
    import pycodestyle as pep8
except ImportError:
    import pep8

from flake8_commas.__about__ import __version__

COMMA_ERROR_CODE = 'C812'
COMMA_ERROR_MESSAGE = 'missing trailing comma'


class CommaChecker(object):
    name = __name__
    version = __version__

    OPENING_BRACKETS = [
        '[',
        '{',
        '(',
    ]

    CLOSING_BRACKETS = [
        ']',
        '}',
        ')',
    ]

    def __init__(self, tree, filename='(none)', builtins=None):
        self.filename = filename

    def get_file_contents(self):
        if self.filename in ('stdin', '-', None):
            self.filename = 'stdin'
            return pep8.stdin_get_value().splitlines(True)
        else:
            return pep8.readlines(self.filename)

    def run(self):
        file_contents = self.get_file_contents()

        noqa_line_numbers = self.get_noqa_lines(file_contents)
        errors = self.get_comma_errors(file_contents)

        for error in errors:
            if error.get('line') not in noqa_line_numbers:
                yield (error.get('line'), error.get('col'), error.get('message'), type(self))

    def get_noqa_lines(self, file_contents):
        tokens = [Token(t) for t in tokenize.generate_tokens(lambda L=iter(file_contents): next(L))]
        return [token.start_row
                for token in tokens
                if token.type == tokenize.COMMENT and token.string.endswith('noqa')]

    def get_comma_errors(self, file_contents):
        tokens = [Token(t) for t in tokenize.generate_tokens(lambda L=iter(file_contents): next(L))]
        tokens = [t for t in tokens if t.type != tokenize.COMMENT]

        valid_comma_context = [False]

        for idx, token in enumerate(tokens):
            if token.string in self.OPENING_BRACKETS:
                valid_comma_context.append(True)

            if token.string in ('for', 'and', 'or') and token.type == tokenize.NAME:
                valid_comma_context[-1] = False

            if (token.string in self.CLOSING_BRACKETS and
                    (idx - 1 > 0) and tokens[idx - 1].type == tokenize.NL and
                    (idx - 2 > 0) and tokens[idx - 2].string != ',' and
                    valid_comma_context[-1]):

                if tokens[idx - 2].string in self.CLOSING_BRACKETS and \
                        tokens[idx - 3].type == tokenize.NL:
                    reverse_idx = idx - 3
                    reverse_token = tokens[reverse_idx]
                    search_idx = self.CLOSING_BRACKETS.index(tokens[idx - 2].string)
                    open_str = self.OPENING_BRACKETS[search_idx]
                    close_str = self.CLOSING_BRACKETS[search_idx]
                    to_open = 0
                    while reverse_token.string != open_str or to_open:
                        if reverse_token.string == close_str:
                            to_open += 1
                        elif reverse_token.string == open_str and to_open:
                            to_open += -1
                        reverse_idx += -1
                        reverse_token = tokens[reverse_idx]
                    if tokens[reverse_idx - 1].string in ['*', '**']:
                        continue
                else:
                    reverse_idx = idx - 1
                    previous_row = []
                    reverse_token = tokens[reverse_idx]
                    while reverse_token.start_row == token.start_row - 1:
                        previous_row.append(reverse_token)
                        reverse_idx += -1
                        reverse_token = tokens[reverse_idx]
                    if previous_row[::-1][0].string in ['*', '**']:
                        continue

                end_row, end_col = tokens[idx - 2].end
                yield {
                    'message': '%s %s' % (COMMA_ERROR_CODE, COMMA_ERROR_MESSAGE),
                    'line': end_row,
                    'col': end_col,
                }

            if token.string in self.CLOSING_BRACKETS:
                valid_comma_context.pop()


class Token:
    '''Python 2 and 3 compatible token'''
    def __init__(self, token):
        self.token = token

    @property
    def type(self):
        return self.token[0]

    @property
    def string(self):
        return self.token[1]

    @property
    def start(self):
        return self.token[2]

    @property
    def start_row(self):
        return self.start[0]

    @property
    def start_col(self):
        return self.start[1]

    @property
    def end(self):
        return self.token[3]

    @property
    def end_row(self):
        return self.end[0]

    @property
    def end_col(self):
        return self.end[1]
