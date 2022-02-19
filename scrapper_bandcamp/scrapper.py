from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import os
import selenium
import time
import pandas as pd



driver = webdriver.Chrome(os.getcwd()+'/chromedriver')
driver.maximize_window()
driver.get('https://bandcamp.com')

time.sleep(2)
titles_element = driver.find_elements_by_class_name("discover-item")

nextPageLink = driver.find_elements_by_class_name("item-page")[-1]
totalPages = int(driver.find_elements_by_class_name("item-page")[-2].get_attribute('innerText'))

titles = []
artist = []
genre = []


print("disabled",nextPageLink.get_attribute("class").split()[-1]=='disabled')

for page in range(0, totalPages):
    driver.get('https://bandcamp.com/?g=all&s=top&p='+str(page)+'&gn=0&f=all&w=0')
    
    time.sleep(1)
    
    titles_element = driver.find_elements_by_class_name("discover-item")
    
    titles = titles + [x.find_element_by_class_name("item-title").get_attribute("text") for x in titles_element]
    artist = artist + [x.find_element_by_class_name("item-artist").get_attribute("text") for x in titles_element]
    genre = genre + [x.find_element_by_class_name("item-genre").get_attribute("innerText") for x in titles_element]
    print(titles,artist,genre)

df = pd.DataFrame({"Title":titles,"Artist":artist,"Genre":genre})
df.to_csv('data_bandcamp.csv', encoding='utf-8',index=False)

print(df)
# print(driver.find_element_by_class_name("item-page").get_attribute("class"))

time.sleep(2)
driver.close()
exit()
