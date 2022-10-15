
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

import pandas as pd

df = pd.DataFrame(columns=['title','company','location','type','time','summary','id','detail'])
driver = webdriver.Chrome(executable_path='C:/Program Files (x86)/Google/Chrome/Application/105.0.5195.127/chromedriver.exe')
driver.implicitly_wait(10)

def getSearchResults(url):
    driver.get(url)
    WebDriverWait(driver, timeout=10)
    cards = driver.find_elements_by_xpath("//div[@class='card search-card']")
    titles = driver.find_elements_by_xpath("//a[@class='card-title-link bold']")
    raw = []

    if len(titles) == len(cards) and len(cards) > 0:
        for card, title in zip(cards, titles):
            row = card.text.split('\n')
            row.remove('Save')
            try:
                row.remove('Easy Apply')
            except:
                ValueError
            if len(row) > 6:
                row.pop(3)  # remove the middle item which is sometimes a single letter
            row.append(title.get_attribute('id'))
            raw.append(row)
        print(len(raw),'...')

    else:
        count = driver.find_element_by_id('totalJobCount').text
        # page_n = int(count) // 100 + 1
        print('... Reached the end and collected a total of {} jobs'.format(count))

    df_ = pd.DataFrame(raw, columns=['title', 'company', 'location', 'type', 'time', 'summary', 'id'])
    return df_


def getJobDetails(id):
    url = "https://www.dice.com/jobs/detail/" + id
    driver.get(url)
    WebDriverWait(driver, timeout=1)

    desc = driver.find_elements_by_id("jobdescSec")
    if len(desc)==1:
        return desc[0].get_attribute("textContent")

    desc = driver.find_elements_by_id("jobDescription")
    if len(desc)==1:
        return desc[0].get_attribute("textContent")

    return ''


search_input = "data software engineer"
query= search_input.replace(' ','%20')
valid_periods = ["","&filters.postedDate=ONE","&filters.postedDate=THREE","&filters.postedDate=SEVEN"]
period = valid_periods[0]
page = 1

while True:
    url = "https://www.dice.com/jobs?q={}&location=Seattle,%20WA,%20USA&latitude=47.6062095&longitude=-122.3320708&countryCode=US&locationPrecision=City&radius=100&radiusUnit=mi&page={}&pageSize=100{}&language=en&eid=S2Q_".format(
        query, page, period)
    df_ = getSearchResults(url)
    if len(df_)>0 :
        df = pd.concat([df, df_],ignore_index=True)
        df.drop_duplicates(subset='id', inplace=True)
        df.to_csv("dice.csv")
        page+=1
    else:
        break


for i in range(0,len(df)-1,1):
    df.loc[i]['detail'] = getJobDetails(df.loc[i]['id'])
    if i % 100==0:
        print(i,"/",len(df))
        df.to_csv("dice.csv")
df.to_csv("dice.csv")

# df['detail'] = df['id'].apply(getJobDetails) # less control

driver.quit()
