"""Contains DsOptions class for DateSense package.
Customizing the directives the parser recognizes and altering what
assumptions it's allowed to make regarding the formatting of date
strings is easy! You can pass your own sets of directive options
and formatting rules to detect_format and other methods. See
methods like get_default_num_options and get_default_rules and the
class attributes they reference, as well as the documentation for
the rules classes and NumOption and WordOption classes for some
examples and thorough descriptions of how things work.
"""
from converter import convert_format
from dstoken import DsToken
from dsrules import *


class DsOptions(object):
    """A DsOptions object contains the data used to track what's possible
    where in a date string and how likely it is.
    Everything you need to go from input to output should be an operation
    of or upon a DsOptions object.
    """

    # Consts for NumOption and WordOption "common" attribute
    UNCOMMON = 1
    COMMON = 2

    class NumOption(object):
        """Contains data representing possible numeric directives."""

        def __init__(self, directive, common, num_range):
            """Constructs a NumOption object.
            Returns the NumOption object.

            :param directive: The directive string, like '%H' or '%y'.
            :param common: The initial score of possibilities for this directive.
                Recommended you use the DsOptions.COMMON and DsOptions.UNCOMMON
                consts.
            :param num_range: Min and max range for values corresponding to this
                directive. Should be indexed - recommended you use a tuple, like
                (1, 31). The value at index 0 will be considered the minimum and
                index 1 the maximum. The range is inclusive.
            """
            self.directive = directive
            self.common = common
            self.num_range = num_range

        def includes_value(self, value):
            """Returns true if the value is valid for this directive, false otherwise."""
            return self.num_range[0] <= value <= self.num_range[1]

    class WordOption(object):
        """ Contains data representing possible alphabetical directives."""

        def __init__(self, directive, common, words, match_length=0):
            """Constructs a WordOption object.
            Returns the WordOption object.

            :param directive: The directive string, like '%B' or '%p'.
            :param common: The initial score of possibilities for this directive.
                Recommended you use the DsOptions.COMMON and DsOptions.UNCOMMON
                consts.
            :param words: A set of possible words that should be considered matches
                for this directive, like ('am', 'pm') for the directive '%p'. These
                strings should be lower case.
            :param match_length: (optional) If partial matches where the encountered
                word matches the start of the full word (e.g. 'mond' matching
                'monday') should be considered valid values for the directive,
                match_length should be the minimum allowed length of those partial
                matches. If match_length is set to 0 (which is the default) then no
                partial matches will be allowed.
            """
            self.directive = directive
            self.common = common
            self.words = words
            self.match_length = match_length

        def includes_value(self, value):
            """Returns true if the value is valid for this directive, false otherwise."""
            value_lower = value.lower()
            if self.match_length and len(value_lower) >= self.match_length:
                for word in self.words:
                    if word.startswith(value_lower):
                        return True
                return False
            else:
                return value_lower in self.words

    # These are the various directives recognized by python.
    # References:
    # http://www.tutorialspoint.com/python/time_strftime.htm
    # https://docs.python.org/2/library/time.html
    # http://pubs.opengroup.org/onlinepubs/009695399/functions/strptime.html

    # Common numeric date directives
    dir_y = NumOption('%y', COMMON, (0, 99))  # 2-digit year
    dir_Y = NumOption('%Y', COMMON, (0, 9999))  # 4-digit year
    dir_m = NumOption('%m', COMMON, (1, 12))  # Month as a number
    dir_d = NumOption('%d', COMMON, (1, 31))  # Day of the month

    # Common numeric time directives
    dir_H = NumOption('%H', COMMON, (0, 23))  # 24-hour
    dir_I = NumOption('%I', COMMON, (1, 12))  # 12-hour
    dir_M = NumOption('%M', COMMON, (0, 59))  # Minutes
    dir_S = NumOption('%S', COMMON, (0, 61))  # Seconds

    # ISO 8601 numeric date directives
    dir_g = NumOption('%g', UNCOMMON, (0, 99))  # 2-digit year corresponding to ISO week number
    dir_G = NumOption('%G', UNCOMMON, (0, 9999))  # 4-digit year corresponding to ISO week number
    dir_V = NumOption('%V', UNCOMMON, (1, 53))  # ISO 8601 week number of the year
    dir_u = NumOption('%u', UNCOMMON, (1, 7))  # Weekday as a number (1-7)

    # Uncommon numeric directives
    dir_j = NumOption('%j', UNCOMMON, (1, 366))  # Day of the year
    dir_C = NumOption('%C', UNCOMMON, (0, 99))  # 2-digit century
    dir_w = NumOption('%w', UNCOMMON, (0, 6))  # Weekday as a number (0-6)
    dir_U = NumOption('%U', UNCOMMON, (0, 53))  # Week number of the year, starting with the first Sunday
    dir_W = NumOption('%W', UNCOMMON, (0, 53))  # Week number of the year, starting with the first Monday

    # Alphabetical directives
    dir_b = WordOption('%b', COMMON,
                       ('jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'))
    dir_B = WordOption('%B', COMMON, (
        'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november',
        'december'))

    dir_p = WordOption('%p', COMMON, ('am', 'pm'))
    dir_a = WordOption('%a', UNCOMMON, ('sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'))
    dir_A = WordOption('%A', UNCOMMON, ('sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'))
    dir_Z = WordOption('%Z', UNCOMMON, ('utc', 'gmt'))  # not a complete list by any means

    # Timezone directive
    dir_z = '%z'  # Special case: Time zones match tokens like +0100 and -0300

    # Default formatting rules, should be suitable for mostly any English-language date format
    # Format rules tell the parser what dates usually look like and how specifically to act on those assumptions.
    # Days, months, years usually delimited by '-' or '/'
    rule_delim_date = DelimiterRule(('%d', '%m', '%y', '%Y'), ('-', '/'), pos_score=2)

    # ISO 8601 date directives should always be adjacent to '-' (or sometimes 'W')
    rule_delim_ISO_date = DelimiterRule(('%G', '%g', '%V', '%u', '%j'), ('-', 'W'), pos_score=2, neg_score=-3)

    # hours, minutes, seconds usually delimited by ':'
    rule_delim_time = DelimiterRule(('%H', '%I', '%M', '%S'), ':', pos_score=2)

    # Year is probably between 1000 and 3000
    rule_range_years = LikelyRangeRule(('%Y', '%G'), (1000, 3000), pos_score=1, neg_score=-1)

    # Century is probably between 10 and 30
    rule_range_cent = LikelyRangeRule('%C', (10, 30), neg_score=-1)

    # Seconds CAN be 60 or 61 due to leap seconds, but that's very rare. Normally it'll be in the range (0, 59).
    rule_range_secs = LikelyRangeRule('%S', (0, 59), neg_score=-1)

    # hh:mm:ss
    rule_pattern_hms = PatternRule((('%H', '%I'), ':', '%M', ':', '%S'), 1, pos_score=3)

    # hh:mm
    rule_pattern_hm = PatternRule((('%H', '%I'), ':', '%M'), 1, pos_score=1)

    # hh:mm<:ss> %p (12-hour with AM/PM)
    rule_pattern_12hr = PatternRule(('%I', '%M', '%p'), 4, pos_score=3)

    # Timezone + offset
    rule_pattern_tz = PatternRule(('%Z', '%z'), 1, pos_score=2)

    # American - months then days then years
    rule_pattern_US_date = PatternRule((('%m', '%b', '%B'), '%d', ('%y', '%Y')), 2, pos_score=4)

    # American - word month then days
    rule_pattern_US_Bd = PatternRule(('%d', ('%m', '%b', '%B'), ('%y', '%Y')), 2, pos_score=3)

    # European - days then months then years
    rule_pattern_EU_date = PatternRule((('%B', '%b'), ' ', '%d'), 1, pos_score=2)

    # European - days then word month
    rule_pattern_EU_dB = PatternRule(('%d', ' ', ('%B', '%b')), 1, pos_score=2)

    # YYYY-MM-DD
    rule_pattern_ymd = PatternRule(('%Y', '-', '%m', '-', '%d'), 1, pos_score=4)

    # Word "day" typically precedes the day
    rule_pattern_verbose_day = PatternRule(('day', '%d'), 4, pos_score=2)

    # Word "month" typically precedes the month
    rule_pattern_verbose_month = PatternRule(('month', ('%m', '%b', '%B')), 4, pos_score=2)

    # Word "year" typically precedes the year
    rule_pattern_verbose_year = PatternRule(('year', ('%Y', '%y')), 4, pos_score=2)

    # Word "time" typically precedes the time
    rule_pattern_verbose_time = PatternRule(('time', ('%H', '%I')), 4, pos_score=2)

    # ISO 8601 date formats often include W%V
    rule_pattern_ISO_W = PatternRule(('W', '%V'), 1, pos_score=2)

    # ISO 8601 date with week number
    rule_pattern_ISO_date = PatternRule((('%G', '%g'), '-', 'W', '%V', '-', '%u'), 1, pos_score=4)

    # ISO 8601 week
    rule_pattern_ISO_week = PatternRule((('%G', '%g'), '-', 'W', '%V'), 1, pos_score=3)

    # ISO 8601 ordinal date
    rule_pattern_ISO_ordinal = PatternRule((('%G', '%g'), '-', '%j'), 1, pos_score=2)

    # 24-hour and 12-hour don't mix
    rule_mutexc_24h_12h = MutualExclusionRule(('%H', ('%I', '%p')), neg_score=-2)

    # No more than one year directive
    rule_mutexc_yr_digits = MutualExclusionRule(('%Y', '%y', '%G', '%g'), neg_score=-2)

    # no sense in both YYYY and century
    rule_mutexc_yr_cent = MutualExclusionRule((('%Y', '%G'), '%C'), neg_score=-2)

    # No more than one month directive
    rule_mutexc_months = MutualExclusionRule(('%B', '%b', '%m'), neg_score=-2)

    # No more than one weekday directive
    rule_mutexc_wkdays = MutualExclusionRule(('%A', '%a', '%u', '%w'), neg_score=-2)

    # No more than one week of year directive
    rule_mutexc_weeks = MutualExclusionRule(('%V', '%U', '%W'), neg_score=-2)

    # These methods are for getting default parser options.
    @staticmethod
    def get_default_num_options():
        """Returns the default set of numeric directive options."""
        return (
            DsOptions.dir_y, DsOptions.dir_Y, DsOptions.dir_m, DsOptions.dir_d,
            DsOptions.dir_H, DsOptions.dir_I, DsOptions.dir_M, DsOptions.dir_S,
            DsOptions.dir_g, DsOptions.dir_G, DsOptions.dir_V, DsOptions.dir_u,
            DsOptions.dir_C, DsOptions.dir_w, DsOptions.dir_j, DsOptions.dir_W, DsOptions.dir_U
        )

    @staticmethod
    def get_default_word_options():
        """Returns the default set of alphabetical directive options."""
        return (
            DsOptions.dir_b, DsOptions.dir_B, DsOptions.dir_p,
            DsOptions.dir_a, DsOptions.dir_A, DsOptions.dir_Z
        )

    @staticmethod
    def get_default_tz_offset_directive():
        """Returns the default timezone offset directive."""
        return DsOptions.dir_z

    @staticmethod
    def get_default_rules():
        """Returns the default set of formatting rules."""
        return (
            DsOptions.rule_delim_date, DsOptions.rule_delim_ISO_date, DsOptions.rule_delim_time,
            DsOptions.rule_range_years, DsOptions.rule_range_cent, DsOptions.rule_range_secs,
            DsOptions.rule_pattern_hms, DsOptions.rule_pattern_hm, DsOptions.rule_pattern_12hr,
            DsOptions.rule_pattern_tz,
            DsOptions.rule_pattern_EU_date, DsOptions.rule_pattern_EU_dB,
            DsOptions.rule_pattern_US_date, DsOptions.rule_pattern_US_Bd,
            DsOptions.rule_pattern_ymd,
            DsOptions.rule_pattern_verbose_day, DsOptions.rule_pattern_verbose_month,
            DsOptions.rule_pattern_verbose_year, DsOptions.rule_pattern_verbose_time,
            DsOptions.rule_pattern_ISO_W, DsOptions.rule_pattern_ISO_date,
            DsOptions.rule_pattern_ISO_week, DsOptions.rule_pattern_ISO_ordinal,
            DsOptions.rule_mutexc_24h_12h, DsOptions.rule_mutexc_yr_digits, DsOptions.rule_mutexc_yr_cent,
            DsOptions.rule_mutexc_months, DsOptions.rule_mutexc_wkdays, DsOptions.rule_mutexc_weeks
        )

    # Constructor
    def __init__(self, format_rules, num_options, word_options, tz_offset_directive):
        """Constructs a DsOptions object.
        Returns the DsOptions object.

        :param format_rules: A set of rule objects such as those found in
            rules which inform the parser of what assumptions it should
            make regarding how input data will normally be formatted.
        :param num_options: A set of NumOption objects to inform the parser of
            possible numeric directives.
        :param word_options: A set of WordOption objects to inform the parser of
            possible alphabetical directives.
        :param tz_offset_directive: Timezone offset directives are a special
            case - this string informs the parser of what directive to use for
            them. (You probably want this to be '%z'.)
        """

        """The allowed attribute tracks what directives are considered to be
                possible and where.
                It contains a list of lists of DsToken objects. The lists contained
                within correspond to each token in the sequence derived from the
                tokenized date string input. The DsToken objects contained within those
                lists represent each possibility being evaluated for the position the
                list corresponds to."""
        self.allowed = []

        """The num_ranges attribute tracks the minimum and maximum encountered
                values for numeric tokens in the date strings.
                This data is used by Likely Range rules. It's a list of lists. The lists
                contained within correspond to each token in the sequence derived from
                the tokenized date string input. Each of those lists contains two items.
                The item at index 0 is the lowest value encountered for the token and
                the item at index 1 is the highest value encountered. If the value at
                an index of num_ranges is None instead of a list, it indicates that no
                numeric values were encountered for the corresponding token."""
        self.num_ranges = []

        self.num_options = num_options
        self.word_options = word_options
        self.tz_offset_directive = tz_offset_directive
        self.format_rules = format_rules

    # These convenience methods simplify the flow of data so that in most cases you won't have to worry about putting
    # the pieces together yourself

    # Initialize and process everything for a data set in one convenient method.
    # Recommended you use this unless you're sure of what you're doing.
    @staticmethod
    def detect_format(dates, format_rules=None, num_options=None, word_options=None, tz_offset_directive=None):
        """Initialize and process everything for a data set in one convenient
        method. (Recommended you use this unless you're sure of what you're
        doing.)
        Returns a DsOptions object containing date format information.

        :param dates: A set of identically-formatted date strings for which
            the formatting should be detected.
        :param format_rules: (optional) A set of rule objects such as those
            found in dsrules which inform the parser of what assumptions it
            should make regarding how input data will normally be formatted.
            Defaults to the value returned by DsOptions.get_default_rules().
        :param num_options: (optional) A set of NumOption objects to inform the
            parser of possible numeric directives. Defaults to the value
            returned by DsOptions.get_default_num_options().
        :param word_options: (optional) A set of WordOption objects to inform
            the parser of possible alphabetical directives. Defaults to the
            value returned by DsOptions.get_default_word_options().
        :param tz_offset_directive: (optional) Timezone offset directives
            are a special case - this string informs the parser of what
            directive to use for them. (You probably want this to be '%z'.)
            Defaults to the value returned by
            DsOptions.get_default_tz_offset_directive().
        """

        # Handle default values for various options
        format_rules = format_rules if format_rules else DsOptions.get_default_rules()
        num_options = num_options if num_options else DsOptions.get_default_num_options()
        word_options = word_options if word_options else DsOptions.get_default_word_options()
        tz_offset_directive = tz_offset_directive if tz_offset_directive else DsOptions.get_default_tz_offset_directive()

        # Do the format detection
        options = DsOptions(format_rules, num_options, word_options, tz_offset_directive)
        options.initialize(dates)
        options.process()

        # All done!
        return options

    def initialize(self, dates):
        """Initialize token possibility data for a set of date strings.

        :param dates: A set of identically-formatted date strings for which
            the formatting should be detected.
        """
        # If it's just one string, turn it into a collection like the methods expect
        if isinstance(dates, ("".__class__, u"".__class__)):
            dates = [dates]
        # Do the initializing
        date_tokens = DsToken.tokenize_date(dates[0])
        self.init_with_date_tokens(date_tokens)
        self.cull_with_dates(dates)
        self.cull_decorators()

    def process(self, dupe_penalty=-2):
        """Process token possibility data for a set of date strings by
        applying rules and checking for duplicate directives.
        Each token possibility will have a score assigned to it which
        represents how likely the parser believes it is to be the correct
        directive or string at that position, relative to the other
        possibilities at that position. (The higher the score, the better the
        fit.)

        :param dupe_penalty: (optional) How the score of duplicate token
            possibilities should be affected, as judged by
            DsOptions.penalize_duplicates().
        """
        self.apply_rules(self.format_rules)
        if dupe_penalty:
            self.penalize_duplicates(dupe_penalty)

    def get_format_tokens(self):
        """Returns a list of the parser's current best guess for what matches each date token."""
        tokens = []
        for token_list in self.allowed:
            max_token = DsToken.get_max_score(token_list)
            if max_token:
                tokens.append(max_token)
        return tokens

    # These methods form the inner clockwork that makes the algorithm function.
    # init_with_date_tokens is what you would call first, to generate an initial list of
    #   possibilities for each token in a date string
    # cull_with_dates is what you would call next, to use a list of date strings to further
    #   inform the parser about what tokens have allowed values for which directives
    # cull_with_date_tokens is called by cull_with_dates on individual tokenized date strings in the list passed to it
    # cull_decorators is what you would call after cull_with_dates, it rids of non-directive
    #   possibilities anywhere that directive possibilities remain
    # apply_rules comes next, it applies a set of rules to the possibility data
    #   (Rules are assumptions the parser is allowed to make regarding how dates should be formatted)
    # penalize_duplicates is what you would call last, it attempts to handle the scenario where a
    #   single directive is considered the most likely in more than one position (It assumes that a
    #   date format ought to have no more than one of each directive)

    def init_with_date_tokens(self, date_tokens):
        """Initialize token possibility data using a single tokenized date.
        The tokenized date string is used to generate a list of possible
        directives at each position, based on whether the value there is
        a possible value for each NumOption and WordOption.

        :param date_tokens: A list of DsToken objects returned by the
            DsToken.tokenize_date() method, where the method's argument
            is a date string.
        """
        token_list_count = len(date_tokens)
        skip = False
        for i in range(0, token_list_count):
            if skip:
                skip = False
            else:
                token = date_tokens[i]
                num_range = None
                # Add the token as a potential decorator
                allowed_here = [DsToken.create_decorator(token.text)]

                if token.is_number():
                    number = int(token.text)
                    for option in self.num_options:
                        if option.includes_value(number):
                            allowed_here.append(DsToken.create_number(option))
                            num_range = [number, number]

                elif token.is_word():
                    for option in self.word_options:
                        if option.includes_value(token.text):
                            allowed_here.append(DsToken.create_word(option))

                if token.is_timezone():
                    allowed_here.append(DsToken.create_timezone(self.tz_offset_directive))

                # Add the list of possibilities for this token to the overall list
                self.allowed.append(allowed_here)
                self.num_ranges.append(num_range)

    def cull_with_dates(self, dates):
        """Cull token possibility data using a set of date strings. The
        values for each token in the date strings are checked against the
        possibilities for that position and if a value is found to lie
        outside the possible values for a directive, that directive is
        discarded as a possibility for the location.

        :param dates: A set of identically-formatted date strings.
        """
        for date in dates:
            date_tokens = DsToken.tokenize_date(date)
            self.cull_with_date_tokens(date_tokens)

    def cull_with_date_tokens(self, date_tokens):
        """Cull token possibility data using a single tokenized date. The
        value for each token in the tokenized date string os checked against
        the possibilities for that position and if a value is found to lie
        outside the possible values for a directive, that directive is
        discarded as a possibility for the location.

        :param date_tokens: A list of DsToken objects returned by the
            DsToken.tokenize_date() method, where the method's argument
            is a date string.
        """
        iterator_range = min(len(self.allowed), len(date_tokens))
        for i in range(0, iterator_range):
            # iterate backwards so we can remove elements without hiccuping
            for j in range(len(self.allowed[i]) - 1, -1, -1):
                token = self.allowed[i][j]

                # if it's not a directive, just check for equivalency
                if token.is_decorator():
                    if token.text != date_tokens[i].text:
                        del self.allowed[i][j]

                # if it is a directive, verify it's the same kind (number/word/timezone)
                elif token.kind != date_tokens[i].kind:
                    del self.allowed[i][j]

                # if it is a directive and it's the right kind, make sure the data fits
                else:
                    # if it's a number, check that this is in the correct range
                    if date_tokens[i].is_number():
                        number = int(date_tokens[i].text)
                        if token.option.includes_value(number):
                            self.num_ranges[i][0] = min(number, self.num_ranges[i][0])
                            self.num_ranges[i][1] = max(number, self.num_ranges[i][1])
                        else:
                            del self.allowed[i][j]

                    # if it's a word, check that it meets the same requirements
                    elif date_tokens[i].is_word():
                        if not token.option.includes_value(date_tokens[i].text):
                            del self.allowed[i][j]

    def cull_decorators(self):
        """Remove non-directive token possibilities where any directive
        possibilities remain at that position."""
        for i in range(0, len(self.allowed)):
            # Check for the presence of both decorator and non-decorator possibilities for this position
            found_dir = False
            found_dec = False
            for tok in self.allowed[i]:
                if not tok.is_decorator():
                    found_dir = True
                else:
                    found_dec = True
                if found_dir and found_dec:
                    break

            # If both directives and decorators are possibilities here, clear out the decorators.
            if found_dir and found_dec:
                # iterate backwards so we can remove elements without hiccuping
                for j in range(len(self.allowed[i]) - 1, -1, -1):
                    tok = self.allowed[i][j]
                    if tok.is_decorator():
                        del self.allowed[i][j]

    def apply_rules(self, rules):
        """Apply all rules in a set to token possibility data.
        Scores for token possibilities will be affected according to the
        assumptions the parser is instructed to make based on the rules
        provided.
        It's worth noting that rules will be evaluated in the order they appear.
        In most cases this won't matter but you may run into unexpected behavior
        if you're not careful about the ordering.
        Delimiter and likely range rules act completely independently of what
        the scores of the possibilities are they can apply to. Pattern rules
        only recognize directives as being eligible for the sequence if their
        score at the time of evaluation is greater than zero. (Non-directive
        strings are not limited in this way.) Mutual exclusion rules decide
        which directive to act in favor of by which has the highest-scoring
        instance.

        :param rules: A set of rule objects, like PatternRule or
            MutualExclusionRule.
        """
        for rule in rules:
            rule.apply(self)

    # This solution isn't perfect but if there are indeed duplicates then the
    # root of the problem probably lies with the rules being used, that they
    # would produce this sort of scenario in the first place.
    def penalize_duplicates(self, dupe_penalty):
        """Try to handle the presence of duplicate high-scoring directives,
        since there's probably no more than one of each directive in any
        given date string.
        The process is this: First, if a possibility is the only high score
        anywhere, its score is affected anywhere it's not the only high score.
        Second, if a possibility is a high score in more than one place, the
        highest-scoring instance out of those is found and the score for that
        directive is affected everywhere else.

        :param dupe_penalty: (optional) How the score of duplicate token
            possibilities should be affected; duplicate possibilities will
            have their scores incremented by this number.
        """
        # First: If a possibility is the only high score anywhere,
        #   reduce its score anywhere it's not the only high score
        # Find where any possibility is the solitary high score
        high_tokens = []
        for token_list in self.allowed:
            high = DsToken.get_all_max_score(token_list)
            if len(high) == 1 and (not high[0].is_decorator()):
                if high[0].text not in high_tokens:
                    high_tokens.append(high[0].text)

        # Now reduce the scores of those possibilities everywhere else
        for token_list in self.allowed:
            high = DsToken.get_all_max_score(token_list)
            if len(high) > 1:
                for tok in token_list:
                    if tok.text in high_tokens:
                        tok.score += dupe_penalty

        # Second: If a possibility is a high score in more than one place:
        # Find the highest-scoring instance as a high score of each possibility (lowest index breaks ties)
        high_tokens = {}
        for token_list in self.allowed:
            high = DsToken.get_all_max_score(token_list)
            for tok in high:
                get_high = high_tokens.get(tok.text, None)
                if not get_high:
                    high_tokens[tok.text] = [tok]
                else:
                    high_tokens[tok.text].append(tok)

        # Affect the score of those possibilities everywhere else
        for key, value in high_tokens.items():
            highest = None
            for tok in value:
                if (not highest) or tok.score > highest.score:
                    highest = tok
            for token_list in self.allowed:
                for tok in token_list:
                    if tok.text == key and tok != highest:
                        tok.score += dupe_penalty

    # These are methods for returning various string representations of this object

    def get_format_string(self, replace_percent=True, blank_if_unrecognized=True, representation=None):
        """Returns the date format as determined by the parser.
        :param replace_percent: (optional) In python date format strings
        literal '%' characters must be represented as '%%'. If this
        argument is set to true, the method will account for stray '%'
        characters by replacing them with '%%'.
        :param blank_if_unrecognized: (optional) If True, a blank string will be returned if either no
            directives were found or if the parser recognized no possibilities for any token. Defaults to True.
        :param representation: (optional) the date string format representation to return.
        """
        string = ''
        tokens = self.get_format_tokens()
        found_dir = False
        valid_tokens = 0
        for token in tokens:
            if replace_percent and token.is_decorator():
                # Literal '%' characters must be represented by '%%' in python date formats
                string += token.text.replace('%', '%%')
            else:
                string += token.text
            found_dir = found_dir or (not token.is_decorator())
            valid_tokens += 1
        if (not blank_if_unrecognized) or (found_dir and (valid_tokens == len(self.allowed))):
            return convert_format(string, representation)
        else:
            return ''

    def get_short_debug_string(self, tok_delimiter=', ', pos_delimiter='\n'):
        """Returns a string representing the highest-scoring possibilities for each token."""
        string = ''
        first_pos = True
        for token_list in self.allowed:
            if first_pos:
                first_pos = False
            else:
                string += pos_delimiter
            if len(token_list):
                first_token = True
                for tok in DsToken.get_all_max_score(token_list):
                    if first_token:
                        first_token = False
                    else:
                        string += tok_delimiter
                    string += str(tok)
            else:
                string += 'NONE'
        return string

    def get_long_debug_string(self, tok_delimiter=', ', pos_delimiter='\n'):
        """Returns a string representing all the possibilities for each token."""
        string = ''
        first_pos = True
        for token_list in self.allowed:
            if first_pos:
                first_pos = False
            else:
                string += pos_delimiter
            if len(token_list):
                first_token = True
                # Sort the list by descending score to make it more immediately readable
                token_list.sort(key=lambda t: -t.score)
                for tok in token_list:
                    if first_token:
                        first_token = False
                    else:
                        string += tok_delimiter
                    string += str(tok)
            else:
                string += 'NONE'
        return string

    # General-purpose casting to string
    def __str__(self):
        return self.get_format_string()

    def __repr__(self):
        return self.get_long_debug_string(',', '; ')
