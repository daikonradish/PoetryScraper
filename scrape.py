#!/bin/env python
    
from bs4 import BeautifulSoup
import re
import urllib2
from time import sleep
    
class PoemScraper:
    
    def __init__(self, seedurl):
        self.visited_sites = set()
        self.stack = []
        self.poetry_data = []
        self.seedurl = seedurl
        self.MAXITER = 100
        self.scrape(seedurl)
    
    ## Takes a poets.org url and scrapes it for information
    def scrape(self, url):
        print "Getting information for {0}...".format(url)
        result = {}
        if "poem" in locals():
            print "Poem exists in locals"
        
        html = urllib2.urlopen(url).read()
        response = html.decode('iso-8859-1')
        
        ## Create our soup! OMNOMNOM.
        try:
            soup = BeautifulSoup(response)
        except Exception, e:
            print "Failed for {0}, because of following error: {1}, moving on to the next.".format(url, e)
            self.scrape_next(url)
                
        ## Text of poem itself is in <pre />
        pres = soup.find_all("pre")
        if len(pres) == 1:
            poem = pres[0].text
        else:
            poem = ""
        
        ## look for poet name... seems standardized enough... always
        ## associated with links to  urls of the form "poet.php something"
        poet = ""
        for alphabet_soup in soup.find_all(href=re.compile("poet.php")):
            if not alphabet_soup.text or not ">" in alphabet_soup.text:
               poet = alphabet_soup.text
        
        ## The two most important things about a poem are the poem itself
        ## and the poet. If we can't get these things, let's just move on.
        if poem and poet:
            ## Likely to be a poem website that points to other poems.
            ## Get URLs.
            self.get_urls(soup)
            
            ## Put poem and poet in the result.
            
            result["poem"] = str(poem)
            result["poet"] = str(poet)
            print ("Poet ({0}) and text of poem scraped. Attemping to get other information from page.".
                     format(result["poet"]))
            
            ## Title of poem is always in <h1 />.
            title = soup.h1.text
            if soup.h1.text:
                result["title"] = str(title)
            
            ## some additional information is available. Poets.org has told us
            ## what the theme is. could be useful for bootstrapping. These are in
            ## tables that are bulleted with the imgSquareBullet.gif image.
            ## OH WWW YOU SUCK SO BAD
            themes = []
            bullets = soup.find_all(src="/images/imgSquareBullet.gif")
            for bullet in bullets:
                about = (bullet.parent
                       .next_sibling.next_sibling.text).strip().lower()
                if about:
                    if about.startswith("poems about"):
                        themes.append(str(about[12:].strip()))
                    elif about.endswith("poems") and not about == "related poems":
                        themes.append(str(about[:-6].strip()))
                    else:
                        continue
            if themes:
                result["themes"] = themes
        
            ## Now look for publishing information. This seems to be after social
            ## media stuff.
            biblio = (soup.find_all(displaytext="Facebook")[0]
                 .find_parent("tr").find_next_siblings("tr"))
            for bib in biblio:
                years = re.findall("([1-2][0-9][0-9][0-9])", bib.text)
                if years:
                    year = int(min(years))
                    result["year"] = year
                
            
            self.poetry_data.append(result)
            print "{0} scraped.".format(url)
            
        self.scrape_next(url)    
    
    def get_urls(self, soup):
        for jumplink in soup.select(".JumpLink"):
            ID = str(jumplink['href']).split('/')[-1]
            if not ID in self.visited_sites:
                self.stack.append(ID)
        print "Obtained links from this page."
    
    def scrape_next(self, currenturl):
        ## Add visited site to set of visited sites.
        self.visited_sites.add(currenturl.split('/')[-1])
        ## Recursion.
        if self.stack or len(self.visited_sites) < self.MAXITER:
            nextID = self.stack.pop()
            nexturl = "http://www.poets.org/viewmedia.php/prmMID/" + nextID
            self.scrape(nexturl)
        else:
            print "Scraped a lot. I'm tired! Stopping now."

## Example usage
new = PoemScraper("http://www.poets.org/viewmedia.php/prmMID/15405")

#!/bin/python
#from bs4 import BeautifulSoup
#import re
#import urllib2
#from time import sleep
#response = urllib2.urlopen("http://www.poets.org/viewmedia.php/prmMID/19794")
#soup = BeautifulSoup(response.read())
#bullets = soup.find_all(src="/images/imgSquareBullet.gif")
#for bullet in bullets:
#    bullet.parent.next_sibling.next_sibling.text.strip().lower()

#response2 = urllib2.urlopen("http://www.poets.org/viewmedia.php/prmMID/20442")
#soup2 = BeautifulSoup(response2.read().decode('iso-8859-1'))
