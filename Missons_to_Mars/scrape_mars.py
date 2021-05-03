import pymongo
import requests
from splinter import Browser
from bs4 import BeautifulSoup as bs
import pandas as pd
import time
from webdriver_manager.chrome import ChromeDriverManager



# DB Setup

client = pymongo.MongoClient('mongodb://localhost:27017')
db = client.mars_db
collection = db.mars 


def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {'executable_path': ChromeDriverManager().install()}
    return Browser('chrome', **executable_path, headless=False)


def scrape():
    browser = init_browser()
    collection.drop()

    # Nasa Mars news
    news_url = 'https://mars.nasa.gov/news/'
    browser.visit(news_url)
    news_html = browser.html
    news_soup = bs(news_html,'html.parser')
    slide_element = news_soup.select_one("ul.item_list li.slide")
    slide_element.find("div", class_="content_title")
    news_title = slide_element.find("div", class_="content_title").get_text()
    news_p = slide_element.find("div", class_="article_teaser_body").get_text()

    # JPL Mars Space Images - Featured Image
    jurl = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(jurl)
    jhtml = browser.html
    jpl_soup = bs(jhtml,"html.parser")
    image_src = jpl_soup.find("img", class_="headerimage fade-in").get("src")
    # base_link = "https:"+jpl_soup.find('div', class_='jpl_logo').a['href'].rstrip('/')
    featured_image_url = f"https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{image_src}"
    featured_image_title = jpl_soup.find('h1', class_="media_feature_title").text.strip()

    # Mars fact
    murl = "https://space-facts.com/mars/"
    mars_df = pd.read_html("https://space-facts.com/mars/")[0]
    print(mars_df)
    mars_df.columns=["Description", "Value"]
    mars_df
    mars_html_table = mars_df.to_html()
    mars_html_table

    # Mars Hemispheres
    mhurl = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(mhurl)  
    mhtml = browser.html 
    mh_soup = bs(mhtml,"html.parser") 
    results = mh_soup.find_all("div",class_='item')
    hemisphere_image_urls = []
    for result in results:
            product_dict = {}
            titles = result.find('h3').text
            end_link = result.find("a")["href"]
            image_link = "https://astrogeology.usgs.gov/" + end_link    
            browser.visit(image_link)
            html = browser.html
            soup= bs(html, "html.parser")
            downloads = soup.find("div", class_="downloads")
            image_url = downloads.find("a")["href"]
            product_dict['title']= titles
            product_dict['image_url']= image_url
            hemisphere_image_urls.append(product_dict)
            
    # Close the browser after scraping
    browser.quit()


    # Return results
    mars_data ={
		'news_title' : news_title,
		'summary': news_p,
        'featured_image': featured_image_url,
		'featured_image_title': featured_image_title,
		'fact_table': mars_html_table,
		'hemisphere_image_urls': hemisphere_image_urls,
        'news_url': news_url,
        'jpl_url': jurl,
        'fact_url': murl,
        'hemisphere_url': mhurl,
        }
    collection.insert(mars_data)