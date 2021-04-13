""" datesense is for determining the format of a date string, or
for a set of many identically-formatted date strings.
For a general-purpose parser that will work for most English-
language date formats, DsOptions.detect_format(dates) will return
an object that you can cast to string (or explicitly call its
get_format_string method) for a date format string for use with
datetime.strptime. For info on how you would go about customizing
the way the parser  works and what assumptions it's allowed to
make regarding the formatting of its input, take a look at the
documentation for DsOptions.py.
"""
from .dsoptions import DsOptions

# datesense version
__version__ = '1.1.0'


def detect_format(dates, format_rules=None, numeric_options=None, word_options=None, tz_offset_directive=None):
    """Initialize and process everything for a data set in one convenient
    method. (Recommended you use this unless you're sure of what you're doing.)
    Returns a DsOptions object containing date format information.

    :param dates: A set of identically-formatted date strings for which the formatting should be detected.
    :param format_rules: (optional) A set of rule objects such as those
        found in dsrules, which inform the parser of what assumptions it
        should make regarding how input data will normally be formatted.
        Defaults to the value returned by DsOptions.get_default_rules().
    :param numeric_options: (optional) A set of NumOption objects to inform the
        parser of possible numeric directives. Defaults to the value
        returned by DsOptions.get_default_num_options().
    :param word_options: (optional) A set of WordOption objects to inform
        the parser of possible alphabetical directives. Defaults to the
        value returned by DsOptions.get_default_word_options().
    :param tz_offset_directive: (optional) Timezone offset directives
        are a special case - this string informs the parser of what
        directive to use for them. (You probably want this to be '%z'.)
        Defaults to the value returned by DsOptions.get_default_tz_offset_directive().
    """
    return DsOptions.detect_format(dates, format_rules, numeric_options, word_options, tz_offset_directive)
