import urllib.parse
import csv
import sys
import time
from pprint import pprint
# import selenium
from selenium import webdriver 
from selenium.webdriver import Chrome 
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.common.by import By
import soupsieve 
from webdriver_manager.chrome import ChromeDriverManager

#Selenium-driver init
#--------------------
# start by defining the options 
options = webdriver.ChromeOptions() 
# options.headless = True # it's more scalable to work in headless mode 
options.add_argument('--headless=new') # it's more scalable to work in headless mode 
options.binary_location = sys.argv[2] if len(sys.argv) == 3 else ''
# normally, selenium waits for all resources to download 
# we don't need it as the page also populated with the running javascript code. 
options.page_load_strategy = 'normal' 
# this returns the path web driver downloaded 
chrome_path = ChromeDriverManager(version="108.0.5359.71").install() #quick fix, Chrome version incompatible
chrome_service = Service(chrome_path) 
# pass the defined options and service objects to initialize the web driver 
driver = Chrome(options=options, service=chrome_service) 
driver.implicitly_wait(5)


def get_song_info(song_url):

    print(song_url)
    song_info = dict()
    
    driver.get(song_url)
    htmlelem = driver.find_element(By.CSS_SELECTOR, "div[class='textContent'")
    name_elem = htmlelem.find_element(By.TAG_NAME, "h1")
    region_elem = htmlelem.find_element(By.TAG_NAME, "h2")
    id_elem = htmlelem.find_element(By.TAG_NAME, "div")
    text_elem = htmlelem.find_element(By.CSS_SELECTOR, "div[class*='lyrics'")#for English: .find_element(By.TAG_NAME, "span")
    # channel_elems = driver.find_element(By.CSS_SELECTOR, "div[class='channel-wrapper']")
    #get song URL
    # r = driver.execute_script("return window.performance.getEntries();")
    # print([res["name"] for res in r if res["name"].endswith(".mp3")][0])
    # safe all scrapped info
    song_info["song_name"] = name_elem.text
    song_info["region"] = region_elem.text
    song_info["id"] = id_elem.text
    song_info["lyrics_raw"] = text_elem.text.strip().replace("\n", "\\n")
    # song_info["audio_url"] = [res["name"] for res in r if res["name"].endswith(".mp3")][0].replace("MIC01", "MICXX")
    # song_info["channel_count"] = len(channel_elems)
    # print(len(channel_elems)) 
    
    return song_info

def scrap_page(song_list, website, songpage):
    driver.get(website)
    songs_on_page = list(map(lambda x: x.text, driver.find_elements(By.CSS_SELECTOR, "div[class='itemId']")))
    for song_id in songs_on_page:
        song_list.append(get_song_info(songpage(song_id)))

def scrap_songs(song_id=None, page_num=None, get_audio=False, delay=0):
    """Scrap songs from polyphonyproject.com and return a list.
    Args:
        song_url (string, optional): if a single specific song needs to be scrapped, specify it's ID. Otherwise, all songs are scrapped. Defaults to None.
        get_audio (bool, optional): if True, also scrap .mp3 files of songs for each channel. Defaults to False.
        delay (int, optional): delay between requests. Defaults to 0.
    Returns:
        song_list (list)
    """
    website = lambda page: f"https://www.polyphonyproject.com/uk/records?SearchResult={page}"
    songpage = lambda id: f"https://www.polyphonyproject.com/uk/song/{id}"
    page_count = 55 #total amount of pages
    song_list = []
    
    # __id = "BMI_UK17050333" 
    # info = get_song_info(songpage(__id))
    # pprint(info)
    
    if page_num != None: #process only one page
        scrap_page(song_list, website(page_num), songpage)
    else:
        for p in range(1, page_count+1):
            scrap_page(song_list, website(p), songpage)
            if delay != 0:
                time.sleep(delay)
    
    
    return song_list

if __name__ == "__main__":
    
    # song_list = [get_song_info("https://www.polyphonyproject.com/uk/song/BMI_UK17050333")]
    song_list = scrap_songs(page_num=int(sys.argv[1]) if len(sys.argv) >= 2 else None)
    
    with open('polyphonyproject_dataset.csv', 'w', encoding='utf8', newline='') as output_file:
        fc = csv.DictWriter(output_file, 
                            fieldnames=song_list[0].keys(),

                        )
        fc.writeheader()
        fc.writerows(song_list)