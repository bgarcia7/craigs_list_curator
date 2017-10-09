import yagmail

class CraigsListCuratorEmailClient:
    
    def __init__(self):
        self.yag = yagmail.SMTP('ccacraigslistscraper', 'ccaroxmys0x')
        
    def build_message(self, results):
        """ Given a list of craigs list results, formats the results into html"""

        message = '<ul>'
        
        output_file = 'output.html'
        f = open(output_file, 'wb')
        for ix, result in enumerate(results):
            try:
		    html = '<li><div>'
		    # add title
		    html += '<h2>' + 'Hit # ' + str(ix + 1) + ': ' + result['title'] + '</h2>'
		    # add price
		    html += '<p>$' + str(result['price']) + '</p>'
		    # add body text
		    html += '<p>' + result['body_text'] + '</p>'
		    # add link
		    html += '<a href="' + result['url'] + '"> Click here to learn more! </a><br/><br/>'
		    # add images
		    html += ''.join(['<img src="' + img + '"/>' for img in result['image_urls']])
		    html += '</div></li><br/>'
                    f.write(html)
                    message += html
            except:
                continue
            
	f.close()
        message += '</ul>'
        return message
    
    def email_results(self, results, email, subject="Your Curated Craig's List Results!"):
        
        try:
            html = self.build_message(results)
            self.yag.send(to=email, subject=subject, contents=[html])
            print '-----> Sent results to {email}'.format(email=email)
        except Exception as e:
            print '-----> Could not email results: {error}'.format(error=str(e))
        
