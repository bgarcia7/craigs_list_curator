from bs4 import BeautifulSoup as soup
from urllib2 import urlopen
from multiprocessing import Pool
from collections import defaultdict
import re
import json
import pickle
import numpy as np
import pathos.pools as pp
from vocabulary.vocabulary import Vocabulary as vb
RESULTS_PER_PAGE = 120

class CraigsListScraper:
    """ Class: CraigsListScraper
        ------------------------
        Given a configuration file, scrapes craigs list and returns a list of post results
    """
    
    def __init__(self):
        self.pool = pp.ProcessPool(50)
    
    def get_page(self, url):

        return soup(urlopen(url), 'lxml')
    
    ################################################################################\
    # Parsing Methods
    ################################################################################
    
    def get_title_info(self, page):

        try:
            # get title text
            title_info = page.find('span',{'class':'postingtitletext'})
            title_text = title_info.find('span',{'id':'titletextonly'}).text

            # get price
            price = title_info.find('span',{'class':'price'})
            price = float(price.text.replace('$','')) if price else None

            # get location
            location = title_info.find('small').text
        except:
            return '', -1, ''

        return title_text, price, location

    def get_body_text(self, page):

        text_body = page.find('section',{'id':'postingbody'}).text.strip()
        text_body_clean = text_body.replace('QR Code Link to This Post','').strip()

        return text_body_clean

    def get_map_info(self, page):

        try:
            map_div = page.find('div',{'id':'map'})
            lat = map_div.get('data-latitude')
            lon = map_div.get('data-longitude')

            return {'lat':lat,'lon':lon}
        except:
            return False

    def get_attr_info(self, page):

        try:
            attr_group = page.find('p',{'class':'attrgroup'})

            # return list of attributes
            return [attr.text for attr in attr_group.findAll('span')]
        except:
            return False

    def get_image_urls(self, page):

        try:
            # find the json describing image_urls
            raw_text = page.find('figure',{'class':'multiimage'}).find('script').text
            image_json = re.findall(r'\[{.*}\]', raw_text)[0]

            # parse image json
            images = json.loads(image_json)

            # return list of image urls
            image_urls = [im['url'] for im in images]

            return image_urls
        except:
            return []

    def get_result_info(self, url):

        try:
            page = self.get_page(url)

            # get basic info -- text, price, location
            title_text, price, location = self.get_title_info(page)
            
            body_text = self.get_body_text(page)

            # get image info
            image_urls = self.get_image_urls(page)

            # get location
            map_info = self.get_map_info(page)

            # get attribute info
            attr = self.get_attr_info(page) 

            return {
                   'title':title_text,
                   'price':price,
                   'location':location,
                   'body_text':body_text,
                   'image_urls':image_urls,
                   'map_info':map_info,
                   'attributes':attr,
                   'url':url
            }
        except Exception as e:
            print e
            return None
        
    ################################################################################\
    # Main Methods for extracting results
    ################################################################################
    
    def get_page_results_info(self, url):
        """ For a given bs4 object, extracts results' info """

        page = self.get_page(url)
        result_urls = [result.find('a').get('href') for result in page.findAll('li',{'class':'result-row'})]
        result_urls = [url for url in result_urls if url]
        result_info = self.pool.map(self.get_result_info, result_urls)
        return result_info
    
    
    def get_all_results(self, url, max_pages=None):
        """ Given a search url, extracts all results. Limited by max_pages. If max_pages = None, pulls everything """

        page = self.get_page(url)
        total_results = int(page.find('span',{'class':'totalcount'}).text)
        pages = [(RESULTS_PER_PAGE*p) for p in range(0, total_results/RESULTS_PER_PAGE + 1)]
        all_page_urls = [url + '&s=' + str(p) for p in pages]
        all_page_urls = all_page_urls[:max_pages] if max_pages else all_page_urls

        # get information for each set of results on each page -- parallelized
        result_info_lists = [self.get_page_results_info(url) for url in all_page_urls]
        result_info_lists = [res_list for res_list in result_info_lists if res_list]
        # flatten results lists
        results_info = [res for res_list in result_info_lists for res in res_list if res]

        return results_info
    
    def get_unique_results(self, results):
        """ Gets unique results keyed on body text """
        
        seen = set()
        final_results = []
        for x in results:
            if x['body_text'] not in seen:
                seen.add(x['body_text'])
                final_results.append(x)
                
        return np.array(final_results)
    
    ################################################################################\
    # Methods for formulating query
    ################################################################################  
    
    def get_min_price(self, price):

        return '&min_price=' + str(price) if price else ''

    def get_max_price(self, price):

        return '&max_price=' + str(price) if price else ''
    
    def get_queries(self, config):
        """ Gets alternate (synonym) queries given single original query """
        
        try:
            alt_query = [x['text'] for x in json.loads(vb.synonym(config['query'])) if x['seq'] == 0][0]
            return [config['query'], alt_query]
        except:
            return [config['query']]
        
    ################################################################################\
    # External Methods
    ################################################################################  
         
    def scrape(self, config, max_results=300):
       	max_results = 200 
        queries = self.get_queries(config)
        info = []
        for query in queries:
            url = config['base_url'] + '/search/sss?query=' + '+'.join(query.split()) 
            url += self.get_min_price(config.get('min_price','')) + self.get_max_price(config.get('max_price',''))

            print url
            print '-----> Scraping: ', query

            info += self.get_all_results(url, max_pages=(max_results/(RESULTS_PER_PAGE*len(queries)) + 1))
            print '-----> Successfully pulled {num} results'.format(num=len(info), query=query)
        
        return self.get_unique_results(info)

