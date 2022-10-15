
import time
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
import pandas as pd

df = pd.DataFrame(columns=['title','company','location','type','time','summary','id','detail'])
driver = webdriver.Chrome(executable_path='C:/Program Files (x86)/Google/Chrome/Application/105.0.5195.127/chromedriver.exe')
driver.implicitly_wait(10)
count=0

# #log in - not needed in this case
# driver.get('https://linkedin.com/')
# ### get username and password input boxes path
# username = driver.find_element_by_xpath('//*[@id="session_key"]')
# password = driver.find_element_by_xpath('//*[@id="session_password"]')
# ### input the email id and password
# username.send_keys("login")
# password.send_keys("password")
# ### click the login button
# login_btn = driver.find_element_by_xpath("//button[@class='sign-in-form__submit-button']")
# login_btn.click()

def getSearchResults(url):
    global count
    driver.get(url)
    WebDriverWait(driver, timeout=10)

    # scrolling sometimes works and sometimes does not work when loading page using selenium
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    print('page open initial height', last_height)

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        print('>scrolling...')
        # Wait to load page
        time.sleep(20)
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print('>breaking...')
            break
        last_height = new_height
        print('>update new height',new_height)

    # Gather all search results
    cards = driver.find_elements_by_xpath("/html/body/div[1]/div/main/section[2]/ul/li")
    raw = []
    if len(cards) > 0:
        for card in cards:
            row = []
            info = card.text.split('\n') #[title, company, location, ..., time]
            id = card.find_element_by_tag_name('div').get_attribute("data-entity-urn").split(':')[-1]  # 'urn:li:jobPosting:3234770919'
            row = info[:3].copy()
            row.extend(['',info[-1],'n/a',id])
            raw.append(row)
        print(len(raw),'/...')
        count +=len(raw)
    else:
        print('... Reached the end and collected a total of {} jobs'.format(str(count)))

    df_ = pd.DataFrame(raw, columns=['title', 'company', 'location', 'type', 'time', 'summary', 'id'])
    return df_


def getJobDetails(id):
    type_, detail_ = '',''
    url = "https://www.linkedin.com/jobs/view/" + id + "/"
    driver.get(url)
    WebDriverWait(driver, timeout=1)

    try:
        desc = driver.find_element_by_xpath("//div[@class='description__text description__text--rich']")
        detail_ = desc.get_attribute("textContent") # job description details
    except NoSuchElementException:
        pass

    try:
        type = driver.find_element_by_xpath("/html/body/main/section[1]/div/div[1]/section[1]/div/ul/li[2]")
        type_= type.find_element_by_tag_name("span").text  # 'Full-time'
    except NoSuchElementException:
        pass

    return type_, detail_


valid_periods=["","&f_TPR=r86400","&f_TPR=r604800","&f_TPR=r2592000"] #[all, today, last week, last month]
period = valid_periods[2] #last 7 days
search_input = "data software engineer"
query= search_input.replace(' ','%20')
count = 0 # increment of 125 per page refresh


while True:
    url = "https://www.linkedin.com/jobs/search/?distance=100{}&geoId=104116203&keywords={}&location=Seattle%2C%20Washington%2C%20United%20States&sortBy=DD&start={}".format(period, query, count)
    df_ = getSearchResults(url)
    if len(df_)>0 :
        df = pd.concat([df, df_],ignore_index=True)
        df.drop_duplicates(subset='id', inplace=True)
        df.to_csv("linkedin.csv")
        print(len(df),count,'\n\n')
    else:
        break


for i in range(0,len(df)-1,1):
    df.loc[i][['type','detail']] = getJobDetails(df.loc[i]['id'])
    if i % 50 ==0:
        print(i,"/",len(df))
        df.to_csv("linkedin.csv")
df.to_csv("linkedin.csv")

len(df)
df['detail'].count()

driver.quit()
