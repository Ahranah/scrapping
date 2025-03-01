import time
from selenium import webdriver
from selenium.webdriver.common.by import By 

import chromedriver_autoinstaller

chromedriver_autoinstaller.install()

driver = webdriver.Chrome() #웹 브라우저가 가진 데이터를 driver에 넣음
driver.get("https://www.youtube.com")
#time.sleep(3) #loading time

selector = " "
group_navigation = driver.find_element(By.CSS_selector, selector)
# navigation : 페이지 이동 및 새로고침
# 1-1. Get() 원하는 페이지로 이동
# 1-2. back() 
# 1-3. forward()
# 1-4. refresh()

# browser information
# 2-1. title, current_url

# driver wait - sleep 은 하드코딩 형태라서 
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

print(group_navigation.text) # print text
group_navigation.click() # click action

input() # python ./machine.py 로 실행하는데 input을 계속 받으니 브라우저 이용 가능
