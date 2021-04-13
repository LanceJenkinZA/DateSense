class PatternRule(object):
    """Pattern rules inform the parser that tokens commonly show
    up in the sequence provided. ('%m','/','%d','/',('%y','%Y'))
    would be one example of such a sequence.
    PatternRule objects that are elements in the format_rules
    attribute of DsOptions objects are evaluated during parsing.
    """

    def __init__(self, sequence, max_distance=1, min_match_score=0, pos_score=0, neg_score=0):
        """Constructs a PatternRule object.
        Positive reinforcement: The scores of possibilities comprising
        a complete sequence as specified are affected. Wildcard tokens
        between specified tokens in the sequence do not have their scores
        affected.
        Negative reinforcement: The scores of directive possibilities
        found in the sequence that were not found to be part of any
        instance of the sequence are affected. Scores of non-directive
        token possibilities are not affected.
        Returns the PatternRule object.

        :param sequence: A set of token possibilities, like
            ('%H',':','%M',':','%S').
        :param max_distance: (optional) How many wildcard tokens are allowed
            to be in between those defined in the sequence. For example,
            the sequence ('%H',':','%M') with a max_distance of 1 would
            match %H:%M but not %H.%M. The sequence ('%H','%M') with a
            max_distance of 2 would match both. Defaults to 1.
        :param min_match_score: (optional) The minimum score a directive
            may have to be considered a potential member of the sequence.
            (Does not apply to non-directive possibilities - those will
            count at any score.) Defaults to 0.
        :param pos_score: (optional) Increment the score of possibilities
            matching the "Positive reinforcement" condition by this much.
            Defaults to 0.
        :param neg_score: (optional) Increment the score of possibilities
            matching the "Negative reinforcement" condition by this much.
            Defaults to 0.
        """
        self.pos_score = pos_score
        self.neg_score = neg_score
        self.sequence = sequence
        self.max_distance = max_distance
        self.min_match_score = min_match_score

    # Positive reinforcement: Possibilities comprising a complete pattern
    # Negative reinforcement: Directive possibilities in the pattern that were not
    #   found to be part of an instance of the pattern
    def apply(self, options):
        """Applies the rule to the provided DsOptions object by affecting token possibility scores."""
        # Which date token in the pattern are we on?
        arg_index = 0
        # How many tokens have we looked over since the last one that's part of the pattern?
        counter = 0
        # What are the token possibilities we've run into so far that fit the pattern?
        ordered_tokens = []
        ordered_tokens_current = []
        # Iterate through the lists of token possibilities
        for token_list in options.allowed:
            # Check if we've passed over the allowed number of in-between tokens yet,
            # if so then reset the pattern search
            if ordered_tokens_current:
                counter += 1
                if counter > self.max_distance:
                    arg_index = 0
                    counter = 0
                    ordered_tokens_current = []
            # Does the token here match the pattern?
            # (Only consider directives with scores greater than or equal to self.min_match_score,
            # and decorators of any score)
            found_token = 0
            for tok in token_list:
                if (tok.score >= self.min_match_score or tok.is_decorator()) and tok.text in self.sequence[arg_index]:
                    ordered_tokens_current.append(tok)
                    found_token += 1
            # One or more possibilities here match the pattern!
            # On to the next expected possibility in the pattern sequence.
            if found_token:
                arg_index += 1
                counter = 0
                # Did we hit the end of the pattern sequence?
                # If so, let's reset so we can see if there's any more occurrences.
                if arg_index == len(self.sequence):
                    arg_index = 0
                    ordered_tokens.extend(ordered_tokens_current)
        # Positive reinforcement
        if self.pos_score:
            for tok in ordered_tokens:
                tok.score += self.pos_score
        # Negative reinforcement
        if self.neg_score:
            # Iterate through all possibilities for all tokens
            for token_list in options.allowed:
                for tok in token_list:
                    # Is the possibility a directive?
                    if not tok.is_decorator():
                        # Does the possibility exist anywhere in the pattern?
                        for match_text in self.sequence:
                            if tok.text in match_text:
                                # Was it not a part of any found instances of the pattern? If so, whack the score.
                                if tok not in ordered_tokens:
                                    tok.score += self.neg_score
