class MutualExclusionRule(object):
    """Mutual exclusion rules indicate that a group of directives
    probably aren't going to show up in the same date string.
    ('%H','%I') would be an example of mutually-exclusive directives.
    MutualExclusionRule objects that are elements in the format_rules
    attribute of DsOptions objects are evaluated during parsing.
    """

    def __init__(self, directives, pos_score=0, neg_score=0):
        """Constructs a MutualExclusionRule object.
        Positive reinforcement: The highest-scoring instance of any of the
        specified possibilities is found and the scores for that same
        possibility at any token where it's present is affected.
        Negative reinforcement: The highest-scoring instance of any of the
        specified possibilities is found and the scores for all the other
        specified possibilities at any token where they're present are
        affected.
        Returns the MutualExclusionRule object.

        :param directives: A set of directives that the rule applies to,
            like ('%H','%I').
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

    # Positive reinforcement: The highest-scoring instance of any of the specified possibilities specified is
    #   found and the scores of that possibility everywhere will be affected
    # Negative reinforcement: The highest-scoring instance of any of the specified possibilities specified is
    #   found and the scores of all the other possibilities will be affected
    def apply(self, options):
        """Applies the rule to the provided DsOptions object by affecting token possibility scores."""
        # Find the highest-scoring instance of each token possibility specified
        matched_tokens = []
        for tok_list in options.allowed:
            for tok in tok_list:
                for i in range(0, len(self.directives)):
                    matched_tokens.append(None)
                    match_text = self.directives[i]
                    if tok.text in match_text:
                        if (not matched_tokens[i]) or tok.score > matched_tokens[i].score:
                            matched_tokens[i] = tok
        # Determine which of the possibilities had the highest score
        highest_tok = None
        highest_index = 0
        for i in range(0, len(matched_tokens)):
            tok = matched_tokens[i]
            if tok and ((not highest_tok) or tok.score > highest_tok.score):
                highest_tok = tok
                highest_index = i
        # Affect scores (Ties go to the lowest-index argument.)
        if highest_tok:
            for tok_list in options.allowed:
                for tok in tok_list:
                    for i in range(0, len(self.directives)):
                        match_text = self.directives[i]
                        if tok.text in match_text:
                            if i == highest_index:
                                # Positive reinforcement
                                tok.score += self.pos_score
                            else:
                                # Negative reinforcement
                                tok.score += self.neg_score
