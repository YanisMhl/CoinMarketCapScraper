from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By 
import pandas as pd
import time
import re

#setup webdriver options
chromeOptions = Options()
chromeOptions.add_experimental_option("detach", True)
chromeOptions.add_experimental_option("excludeSwitches", ["enable-logging"])

web = "https://coinmarketcap.com/"
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chromeOptions)
driver.get(web)

#Waiting for the website to load
time.sleep(0.5)

#Retrieve the title, table and categories of the website
title = driver.find_element(By.XPATH, "//h1").text
print(title)
table = driver.find_element(By.XPATH, "//table")
categories = driver.find_elements(By.XPATH, "//tr")[0].text.split("\n")[1:-1]

#Generate a dictionary containing all the categories we have retrieved from the website
cryptoTable = {}
for category in categories:
    cryptoTable[category] = []
print(cryptoTable)



#Pagination
pagination = driver.find_elements(By.XPATH, "//ul[contains(@class, 'pagination')]")[1]
nextPageButton = pagination.find_element(By.XPATH, ".//a[contains(@aria-label, 'Next page')]")
# pageNumber = int(pagination.find_elements(By.XPATH, ".//li[contains(@class, 'page')]")[-1].text)
pageNumber = 10
current_page = 1

#The site being asynchronous, it is good to cut the page into 15 steps that we scroll turn by turn
page_height = driver.execute_script("return document.body.scrollHeight")
page_step = page_height // 15
page_steps = []
for i in range(page_step, page_height, page_step):
    page_steps.append(i)

while current_page <= pageNumber:
    
    print(f"page {current_page}/{pageNumber}")
        
    current_step = 0

    #scroll loop
    for step in page_steps:
        time.sleep(0.5)
        driver.execute_script(f"window.scrollTo({current_step}, {step})")
        print(f"Scrolled to {current_step}/{page_steps[-1]}")
        current_step = step 

    time.sleep(5)
    cryptoRows = driver.find_elements(By.XPATH, "//tr")[1:]

    for i, cryptoRow in enumerate(cryptoRows):
        
        cryptoData = cryptoRow.find_elements(By.XPATH, ".//td")[2:-2]
        for i, cryptoCell in enumerate(cryptoData):
            cryptoCellText = cryptoCell.text
            try:
                class_name = cryptoCell.find_element(By.XPATH, ".//*/*").get_attribute("class")
            except:
                class_name = "no class found"
            
            if class_name == "icon-Caret-up":
                cryptoCellText = f"+{cryptoCellText}"
            elif class_name == "icon-Caret-down":
                cryptoCellText = f"-{cryptoCellText}"
            
            match = re.search(r"(.+)\n(.+)", cryptoCellText)
            if match:
                cryptoCellText = "{} ({})".format(match.group(1), match.group(2))
            
            
            print("collecting data..")
            cryptoTable[categories[i]].append(cryptoCellText)

    nextPageButton.click()
    current_page += 1

for key, value in cryptoTable.items():
    print(f"{key} : {len(value)}")
        
print(cryptoTable)

df_crypto = pd.DataFrame(cryptoTable)
df_crypto.to_csv("crypto.csv", index=False)