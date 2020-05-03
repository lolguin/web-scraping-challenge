#import dependencies
import pandas as pd
from bs4 import BeautifulSoup as bs
from splinter import Browser
from splinter.exceptions import ElementDoesNotExist
import requests
import time

def init_browser():
    executable_path = {'executable_path': 'C:/Users/lolgu/bin/chromedriver.exe'}
    return Browser("chrome", **executable_path, headless=True)

def scrape():

    #enable chrome browser
    browser = init_browser()
    #create dictionary to store mars data that we'll scrape
    mars_data = {}

    #assign URLs
    nasa_url= 'https://mars.nasa.gov/news/'
    jpl_image_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    nasa_twitter_url = 'https://twitter.com/marswxreport?lang=en'
    mars_facts_url = 'https://space-facts.com/mars/'
    usgs_image_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'

    ### 1) Retrieve NASA MARS News ###

    #retrieve the page using requests
    #nasa_response = requests.get(nasa_url)
    browser.visit(nasa_url)
    time.sleep(3)    
    
    nasa_response = browser.html
       

    #create a soup variable for nasa url
    nasa_soup = bs(nasa_response, 'lxml')

    nasa_results = nasa_soup.find('li', class_='slide')

    for x in nasa_results:
        news_body = x.find('div', class_='rollover_description_inner').text
        news_title = x.find('div', class_= 'content_title').text

    #Load news title and body to dictionary
    mars_data['news_title'] = news_title
    mars_data['news_body'] = news_body

    ### 2) Retrieve JPL Image ###

    base_url = 'https://jpl.nasa.gov'
    browser.visit(jpl_image_url)
    jpl_response = browser.html

    #create a soup variable for nasa url
    jpl_soup = bs(jpl_response, 'lxml')

    browser.click_link_by_id('full_image')

    browser.click_link_by_partial_text('more info')

    #reset html and soup
    jpl_response = browser.html
    jpl_soup = bs(jpl_response, 'lxml')

    images = jpl_soup.find_all('img', class_='main_image')

    for image in images:
        jpl_image = base_url + image['src']
        
    mars_data['jpl_image'] = jpl_image

    ### 3) Retrieve MARS Weather ###

    #use requests to navigate to nasa twitter url
    response = requests.get(nasa_twitter_url)
    twitter_soup = bs(response.text, 'lxml')

    #create list to store tweets
    tweets = []

    #loop through content and store tweets in tweets list
    for tweet in twitter_soup.find_all('div', class_='content'):
        tweets.append(tweet.find('div',class_='js-tweet-text-container').find('p').text)

    #assign 1st tweet to mars weather variable
    mars_data['mars_weather'] = tweets[0]

    ### 4) Retrieve MARS Facts ###

    #use pandas read_html to pull the tables from this webpage
    facts_tables = pd.read_html(mars_facts_url)

    #set 1st index as dataframe
    facts_df = facts_tables[0]

    #set 1st column as df index
    facts_df.set_index([0])

    #convert and export data frame to HTML file
    html = facts_df.to_html(index=False, header=False)

    mars_data['facts'] = html

    ### Retrieve MARS Hemispheres ###

    base_url = 'https://astrogeology.usgs.gov/'
    browser.visit(usgs_image_url)
    usgs_response = browser.html

    #create a soup variable for nasa url
    usgs_soup = bs(usgs_response, 'lxml')

    #create empty lists and dictionaries
    title = []
    url = []
    img_url = []

    #pull title names and append to title list
    for item in usgs_soup.find_all('div', class_='item'):
        title.append(item.find('h3').text)

    #find all item links
    links = usgs_soup.find_all('a', class_='itemLink product-item', href=True)

    #grab url and append to url list
    for link in links:
        if link.text:
            x = base_url + link['href']
            url.append(x)

    #loop through each url to grab image link
    for page in url:
        browser.visit(page)
        url_response = browser.html
        url_soup = bs(url_response, 'lxml')
        
        #find all divs with downloads class
        divs = url_soup.find_all('div', class_= 'downloads')
        
        #loop through divs to find img urls
        for div in divs:
            image = div.find('a')['href']
            img_url.append(image)
        
    #create final dictionary and list to hold dictionary
    mars_dict = {}
    hemisphere_image_urls = []

    #loop through title and img_url lists and append to dictionary
    for x in range(len(title)):
        mars_dict = {}
        mars_dict['title'] = title[x]
        mars_dict['img_url'] = img_url[x]
        hemisphere_image_urls.append(mars_dict)
    
    #store final list of dictionaries into mars_data
    mars_data['hemi_img_url'] = hemisphere_image_urls

    return mars_data

if __name__ == "__main__":
    print("\nTesting Data Retrieval:....\n")
    print(scrape())  