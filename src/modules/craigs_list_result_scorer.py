import numpy as np

class CraigsListResultScorer:
    """ Class: CraigsListResultScorer:
        -------------------
        Takes Craig's list postings and a configuration file. 
        
        Sorts postings by most relevsant based on a user's needs and preferences
    """
    
    def __init__(self):
        pass
    
    def get_score(self, config, result):
        """ Gets score for craigslist posting """
        
        interests = config['interests']
        required = config['required'] + [config['query']]

        title = result['title']
        body = result['body_text']

        # make sure all required terms appear
        for term in required:
            if term not in title and term not in body:
                return 0

        # scoring function
        score = 0
        for words in interests:
            score += 6 if words in title else 0
            score += 2 if words in body else 0

            words = words.split()
            score += np.sum([2 if word in title else 0 for word in words])
            score += np.sum([1 if word in body else 0 for word in words])
        return score