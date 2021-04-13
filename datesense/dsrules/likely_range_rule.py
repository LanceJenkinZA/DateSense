from dstoken import DsToken


class LikelyRangeRule(object):
    """Likely range rules mean that a numeric directive is most
    likely to be present for only a subset of its strictly possible
    values.
    LikelyRangeRule objects that are elements in the format_rules
    attribute of DsOptions objects are evaluated during parsing.
    """

    def __init__(self, directives, likely_range, pos_score=0, neg_score=0):
        """Constructs a LikelyRangeRule object.
        Positive reinforcement: The scores of specified directives where
        the encountered values are all within the likely range are
        affected.
        Negative reinforcement: The scores of specified directives where
        any of the encountered values lie outside the likely range are
        affected.
        Returns the LikelyRangeRule object.

        :param directives: A directive or set of directives that the rule
            applies to, like '%S'.
        :param likely_range: Min and max range that any values for the
            specified directives are likely to be within. Should be indexed -
            recommended you use a tuple, like (0, 59). The value at index 0
            will be considered the minimum and index 1 the maximum. The
            range is inclusive.
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
        self.likely_range = likely_range

    # Positive reinforcement: Directives inside the likely range
    # Negative reinforcement: Directives outside the likely range
    def apply(self, options):
        """Applies the rule to the provided DsOptions object by affecting token possibility scores."""
        # Iterate through the token possibilities
        tok_list_count = len(options.allowed)
        for i in range(0, tok_list_count):
            tok_list = options.allowed[i]
            for tok in tok_list:
                # If the possibility is a number and matches the argument, check whether the encountered
                # data was all inside the likely range.
                if tok.kind == DsToken.KIND_NUMBER and tok.text in self.directives:
                    if (options.num_ranges[i][0] >= self.likely_range[0] and
                            options.num_ranges[i][1] <= self.likely_range[1]):
                        # Positive reinforcement
                        tok.score += self.pos_score
                    else:
                        # Negative reinforcement
                        tok.score += self.neg_score
