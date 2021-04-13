from dstoken import DsToken


class DelimiterRule(object):
    """Delimiter rules mean that if some tokens are separated by a
    delimiter, assumptions can be made for what those tokens represent.
    DelimiterRule objects that are elements in the format_rules
    attribute of DsOptions objects are evaluated during parsing.
    """

    def __init__(self, directives, delimiters, pos_score=0, neg_score=0):
        """Constructs a DelimiterRule object.
        Positive reinforcement: The scores of specified possibilities that
        are adjacent to one or more tokens where any of the specified
        delimiters are a possibility are affected.
        Negative reinforcement: The scores of specified possibilities that
        are not adjacent any tokens where any of the specified delimiters
        are a possibility are affected.
        Returns the DelimiterRule object.

        :param directives: A directive or set of directives that the rule
            applies to, like ('%H','%I','%M','%S').
        :param delimiters: A delimiter or set of delimiters that the rule
            applies to, like ':'.
        :param pos_score: (optional) Increment the score of possibilities
            matching the "Positive reinforcement" condition by this much.
            Defaults to 0.
        :param neg_score: (optional) Increment the score of possibilities
            matching the "Negative reinforcement" condition by this much.
            Defaults to 0.
        """
        self.pos_score = pos_score
        self.neg_score = neg_score
        self.directives = directives
        self.delimiters = delimiters

    # Positive reinforcement: Specified possibilities that are adjacent to one of the specified delimiters
    # Negative reinforcement: Specified possibilities that are not adjacent to one of the specified delimiters
    def apply(self, options):
        """Applies the rule to the provided DsOptions object by affecting token possibility scores."""
        adjacent = []
        # For each delimiter specified:
        for delimiter in self.delimiters:
            tok_list_count = len(options.allowed)
            # Determine which date tokens are adjacent to any one that has the delimiter text as a possibility
            for i in range(0, tok_list_count):
                tok_list = options.allowed[i]
                delim_tok = DsToken.get_token_with_text(tok_list, delimiter)
                if delim_tok:
                    if i > 0 and (options.allowed[i - 1] not in adjacent):
                        adjacent.append(options.allowed[i - 1])
                    if i < tok_list_count - 1 and (options.allowed[i + 1] not in adjacent):
                        adjacent.append(options.allowed[i + 1])
        # Affect scores of possibilities specified
        for tok_list in options.allowed:
            # Positive reinforcement
            if tok_list in adjacent:
                if self.pos_score:
                    for tok in tok_list:
                        if tok.text in self.directives:
                            tok.score += self.pos_score
            # Negative reinforcement
            elif self.neg_score:
                for tok in tok_list:
                    if tok.text in self.directives:
                        tok.score += self.neg_score
