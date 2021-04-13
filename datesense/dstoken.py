"""Contains DsToken class for DateSense package."""


# Used by the parser for keeping track of what goes where, and what can possibly go where
class DsToken(object):
    """DsToken objects are used by the parser for keeping track of what
    goes where in tokenized date strings, and what can possibly go where
    in format strings as determined by a DsOptions options.
    In the context of tokenized date strings: each DsToken object
    contains information on what's actually there in the string.
    In the context of DsOptions allowed lists: each DsToken object
    contains information on what directives (or non-directive strings)
    are allowed to go where, and how likely the parser thinks each must
    be. (The higher a DsToken's score, the more likely it's considered
    to be.)
    """

    # Consts for the different kinds of tokens recognized
    KIND_DECORATOR = 0
    KIND_NUMBER = 1
    KIND_WORD = 2
    KIND_TIMEZONE = 3

    # Const for number of characters timezone offset numbers are expected to be,
    # e.g. +0100 or -0300 (You definitely want this value to be 4.)
    TIMEZONE_LENGTH = 4

    def __init__(self, kind, text, option=None):
        """Constructs a DsToken object.
        You probably want to be using the kind-specific constructors
        instead of this one: create_decorator, create_number,
        create_word, and create_timezone.
        Returns the DsToken object.

        :param kind: The DsToken kind, which should be one of
            DsToken.KIND_DECORATOR, DsToken.KIND_NUMBER,
             DsToken.KIND_WORD, DsToken.KIND_TIMEZONE.
        :param text: A string to associate with this this object.
        :param option: (optional) A NumOption or WordOption object to
            associate with this object. Defaults to None.
        """
        self.kind = kind
        self.text = text
        self.option = option
        if option:
            self.score = option.common
        else:
            self.score = 0

    @staticmethod
    def create_decorator(text):
        """Constructs a DsToken object for a decorator token.
        Decorator token possibilities are those which correspond to
        no directive. For example, the ':' characters in '%H:%M:%S'.
        Returns the DsToken object.

        :param text: A string to associate with this this object.
        """
        return DsToken(DsToken.KIND_DECORATOR, text, None)

    @staticmethod
    def create_number(option):
        """Constructs a DsToken object for a numeric token.
        Returns the DsToken object.

        :param option: A directive option to associate with this this
            object and to derive its text attribute from. Should be a
            NumOption object.
        """
        return DsToken(DsToken.KIND_NUMBER, option.directive, option)

    @staticmethod
    def create_word(option):
        """Constructs a DsToken object for an alphabetical token.
        Returns the DsToken object.

        :param option: A directive option to associate with this this
            object and to derive its text attribute from. Should be a
            WordOption object.
        """
        return DsToken(DsToken.KIND_WORD, option.directive, option)

    @staticmethod
    def create_timezone(directive):
        """Constructs a DsToken object for a timezone offset token.
        Returns the DsToken object.

        :param directive: A string to associate with this this object.
            (You probably want this to be '%z'.)
        """
        return DsToken(DsToken.KIND_TIMEZONE, directive, None)

    def __str__(self):
        kinds = "dec", "num", "word", "tz"
        return kinds[self.kind] + ":'" + self.text + "'(" + str(self.score) + ")"

    def __repr__(self):
        return self.__str__()

    # Simple methods for checking whether the token is a specific kind

    def is_decorator(self):
        """Returns true if the DsToken is for a decorator, false otherwise."""
        return self.kind == DsToken.KIND_DECORATOR

    def is_number(self):
        """Returns true if the DsToken is for a numeric directive, false otherwise."""
        return self.kind == DsToken.KIND_NUMBER

    def is_word(self):
        """Returns true if the DsToken is for an alphabetical directive, false otherwise."""
        return self.kind == DsToken.KIND_WORD

    def is_timezone(self):
        """Returns true if the DsToken is for a timezone offset directive, false otherwise."""
        return self.kind == DsToken.KIND_TIMEZONE

    @staticmethod
    def tokenize_date(date_string):
        """Tokenizes a date string.
        Tokens are divided on the basis of whether each character is
        a letter, a digit, or neither. (With some special handling to
        combine tokens like '+' and '0100' or '-' and '0300' into one
        timezone offset token.) For example, the string '12 34Abc?+1000'
        would be tokenized like so: '12', ' ', '34', 'Abc', '?', '+1000'.
        Returns a list of DsToken objects.

        :param date_string: The date string to be tokenized.
        """

        current_text = ''
        current_kind = -1
        tokens = []

        # Iterate through characters in the date string, divide into tokens and assign token kinds.
        # Digits become number tokens, letters become word tokens, four-digit numbers preceded
        # by '+' or '-' become timezone tokens. Everything else becomes decorator tokens.
        for char in date_string:
            asc = ord(char)
            is_digit = (48 <= asc <= 57)  # 0-9
            is_alpha = (97 <= asc <= 122) or (65 <= asc <= 90)  # a-zA-Z
            is_tzoff = (43 == asc or asc == 45)  # +|-
            tokkind = DsToken.KIND_NUMBER * is_digit + DsToken.KIND_WORD * is_alpha + DsToken.KIND_TIMEZONE * is_tzoff
            if tokkind == current_kind and current_kind != DsToken.KIND_TIMEZONE:
                current_text += char
            else:
                if current_text:
                    tokens.append(DsToken(current_kind, current_text))
                current_kind = tokkind
                current_text = char
        if current_text:
            tokens.append(DsToken(current_kind, current_text))

        # Additional pass for handling timezone tokens
        ret_tokens = []
        skip = False
        tokens_count = len(tokens)
        for i in range(0, tokens_count):
            if skip:
                skip = False
            else:
                tok = tokens[i]
                if tok.is_timezone():
                    token_previous = tokens[i - 1] if (i > 0) else None
                    token_next = tokens[i + 1] if (i < tokens_count - 1) else None
                    check_prev = (not token_previous) or not (token_previous.is_number() or token_previous.is_timezone())
                    check_next = (token_next and token_next.is_number() and
                                  len(token_next.text) == DsToken.TIMEZONE_LENGTH)
                    if check_prev and check_next:
                        tok.text += token_next.text
                        skip = True
                    else:
                        tok.kind = DsToken.KIND_DECORATOR
                ret_tokens.append(tok)

        # All done!
        return ret_tokens

    # Convenience functions for doing useful operations on sets of token possibilities  

    @staticmethod
    def get_token_with_text(token_list, text):
        """Returns the first token in a set matching the specified text.

        :param token_list: A list of DsToken objects.
        :param text: The text to search for.
        """
        for tok in token_list:
            if tok.text in text:
                return tok
        return None

    @staticmethod
    def get_max_score(token_list):
        """Returns the highest-scoring token in a set.
        In case of a tie, the lowest-index token will be returned.

        :param token_list: A list of DsToken objects.
        """
        high = None
        for tok in token_list:
            if (not high) or tok.score > high.score:
                high = tok
        return high

    @staticmethod
    def get_all_max_score(toklist):
        """Returns a list of the highest-scoring tokens in a set."""
        high = []
        for tok in toklist:
            if (not high) or tok.score > high[0].score:
                high = [tok]
            elif tok.score == high[0].score:
                high.append(tok)
        return high
