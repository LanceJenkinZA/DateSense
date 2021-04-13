from .formats import moment

converters = {
    "python": None,
    "moment": moment.mapping
}


def convert_format(format_string, mapping):
    """ Convert the format string using the desired mapping."""
    if mapping in converters:
        for token, conversion in converters[mapping].items():
            format_string = format_string.replace(token, conversion)

    return format_string
