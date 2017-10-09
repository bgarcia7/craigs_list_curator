import sys
sys.path.append('./modules')

from config import config
from craigs_list_scraper import CraigsListScraper
from craigs_list_result_scorer import CraigsListResultScorer
from craigs_list_curator_email_client import CraigsListCuratorEmailClient
import numpy as np

if __name__ == "__main__":
        
    # scrape information (harvest)
    scraper = CraigsListScraper()
    info = scraper.scrape(config, max_results=1000)

    # get top results (process)
    scorer = CraigsListResultScorer()
    result_scores  = np.array([scorer.get_score(config, result) for result in info])
    result_ixs = np.argsort(result_scores)[::-1][:config['num_results']]
    results = info[result_ixs]

    # email results (deliver value)
    client = CraigsListCuratorEmailClient()        
    client.email_results(results, email=config['email'])
