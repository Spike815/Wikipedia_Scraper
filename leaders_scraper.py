import json
import requests
from requests import Session
import re
from bs4 import BeautifulSoup

def get_leaders():
    """
    This function send requests to country-leaders API, and use the returned response to scrap corresponding 
    paragraph on wikipedia page. The return value is a dictionary.
"""
    cookies_url = "https://country-leaders.onrender.com/cookie/"
    leaders_url = "https://country-leaders.onrender.com/leaders"
    countries_url = "https://country-leaders.onrender.com/countries"
    #start a session
    s = requests.Session()

    #get cookies from api
    req = s.get(cookies_url)

    #get countries from api
    countries = s.get(countries_url,cookies = req.cookies).json()
    leaders_per_country = {}


    #loop through the country list, get the first paragraph on wikipedia, append it to the dictionary 
    for country in countries:
        if s.get(leaders_url,params={'country':'us'},cookies=req.cookies).status_code == 200:
            leaders_per_country[country] = s.get(leaders_url,params={'country':country},cookies=req.cookies).json()
            for leader in leaders_per_country[country]:
                leader['first_paragraph'] = get_first_paragraph(leader['wikipedia_url'],s)
        else:
            req = s.get(cookies_url)
            leaders_per_country[country] = s.get(leaders_url,params={'country':country},cookies=req.cookies).json()
            for leader in leaders_per_country[country]:
                leader['first_paragraph'] = get_first_paragraph(leader['wikipedia_url'],s)
            
    return leaders_per_country

def get_first_paragraph(wikipedia_url:str,session:Session):
    """
  This function takes two paramenters: url and session, 
  and returns the first paragraph on the wikipedia
  page as a string.
  
  """   
    r = session.get(wikipedia_url).text
    first_paragraph = ''
    paragraphs = []
    soup = BeautifulSoup(r,'html.parser')
    #define the regex to clean up the string
    reg = r"\[([a-z\s\.]*\d+)\]"
    reg2 = r"\[([a-z])|([\.]*)\]"

    # use a for loop, check if the parent tag of the paragraph
    for elem in soup.find_all('p'):
        # if the parent tag of the paragraph is a table or div with class name 'bandeau-cell'
        # then it's not the target paragraph
        if elem.find_parent('table') or elem.find_parent('div',{'class':'bandeau-cell'}):
            continue
        paragraphs.append(elem.text)

    #loop through all paragraphs, the aimmed 'first paragraph' should be in the index 0 or 1
    #if index 0 return none, then index 1 is the targetted paragraph
    #clean the text with regex
    for text in paragraphs:
        if text.split() :
            temp = re.sub(reg, "",text)
            first_paragraph = re.sub(reg2,"",temp)
            break
    return first_paragraph

def save(file:dict):
    """
    This function takes a dictionary as parameter, 
    and write it into a json file named "leaders_per_country.json".
    """
    #make sure non-ascii charactors are reserved
    json_file = json.dumps(file, ensure_ascii=False)
    with open('leaders_per_country.json','w',encoding="utf-8") as outputfile:
        outputfile.write(json_file)

save(get_leaders())

