import yagmail

class CraigsListCuratorEmailClient:
    
    def __init__(self):
        self.yag = yagmail.SMTP('ccacraigslistscraper', 'ccaroxmys0x')
        
    def build_message(self, results):
        """ Given a list of craigs list results, formats the results into html"""

        message = '<ul>'
        
        for ix, result in enumerate(results):
            message += '<li><div>'
            # add title
            message += '<h2>' + 'Hit # ' + str(ix + 1) + ': ' + result['title'] + '</h2>'
            # add price
            message += '<p>$' + str(result['price']) + '</p>'
            # add body text
            message += '<p>' + result['body_text'] + '</p>'
            # add link
            message += '<a href="' + result['url'] + '"> Click here to learn more! </a><br/><br/>'
            # add images
            message += ''.join(['<img src="' + img + '"/>' for img in result['image_urls']])
            message += '</div></li><br/>'
            
        message += '</ul>'
        return message
        
    def email_results(self, results, email, subject="Your Curated Craig's List Results!"):
        
        try:
            contents = [self.build_message(results)]
            self.yag.send(to=email, subject=subject, contents=contents)
            print '-----> Sent results to {email}'.format(email=email)
        except Exception as e:
            print '-----> Could not email results: {error}'.format(error=str(e))
        