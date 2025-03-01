#https://m.blog.naver.com/draco6/221664143794

import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
import requests
import time
import shutil
import json
import re
import os
import pandas as pd 



def handle_popup(driver, popup_class="pop-alert", button_text="확인", wait_time=5):

    try:   
        # 팝업 요소 찾기
        popup = WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((By.CLASS_NAME, popup_class))
        )
        
        # 팝업 내부의 버튼 찾기
        confirm_button = popup.find_element(By.XPATH, f".//button[span[text()='{button_text}']]")
        confirm_button.click()
        print("✅ 확인 버튼 클릭 성공")
        return True

    except Exception as e:
        print(f"❌ 팝업 처리 실패: {e}")
        return False

def login_to_site(driver, username, password, login_button_class="header-login-idcr", username_field_id="idModel", password_field_id="pwModel", submit_button_class="btn-login", user_confirm_class="user-nm", wait_time=3):

    try:
        print("🔍 로그인 버튼 클릭 시도")
        # 로그인 버튼 클릭
        login_button = WebDriverWait(driver, wait_time).until(
            EC.element_to_be_clickable((By.CLASS_NAME, login_button_class))
        )
        login_button.click()

        # 사용자 아이디 및 비밀번호 필드 대기
        username_field = WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((By.ID, username_field_id))
        )
        password_field = driver.find_element(By.ID, password_field_id)

        # 사용자 아이디 및 비밀번호 입력
        username_field.click() 
        username_field.clear()
        password_field.click()  
        password_field.clear()
        username_field.send_keys(username)
        password_field.send_keys(password)

        print("✅ 로그인 정보 입력 완료")

        # 로그인 제출 버튼 클릭
        submit_button = driver.find_element(By.CLASS_NAME, submit_button_class)
        submit_button.click()
        print("🔍 로그인 버튼 클릭 중...")

        # 로그인 성공 확인
        WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((By.CLASS_NAME, user_confirm_class))
        )
        print("✅ 로그인 성공!")
        return True

    except Exception as e:
        print(f"❌ 로그인 실패: {e}")
        return False

def navigate_to_financial_page(driver, search_key, wait_time=10):

    try:
        # 검색 필드 요소 찾기
        search_input = WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='검색어를 입력해주세요.']"))
        )
        
        # 검색어 입력
        search_input.clear()
        search_input.send_keys(search_key)

        # 검색 버튼 클릭
        search_button = WebDriverWait(driver, wait_time).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@title='검색하기']"))
        )
        search_button.click()
        print("✅ 검색 버튼 클릭 완료")
        time.sleep(1)

    except Exception as e:
        print(f"❌ 검색 단계 실패: {e}")
        return False

    # 요소 탐색 및 클릭
    li_index = 1
    found = False

    while True:
        try:
            # 기업명으로 찾기
            name_xpath = f"//*[@id='et-area']/div/div[2]/ul/li[{li_index}]/div/button/span"
            # 사업자번호로 찾기
            code_xpath = f"//*[@id='et-area']/div/div[2]/ul/li[{li_index}]/div/ul[1]/li[4]/span[2]"
            span_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, code_xpath))
            )
            
            # 찾은 텍스트와 검색어 비교
            if search_key in span_element.text.strip():
                print(f"✅ '{search_key}' 찾음!")
                found = True
                break
            else:
                li_index += 1

        except Exception as e:
            print(f"❌ 찾을 수 있는 항목이 없습니다. (오류: {e})")
            break
            
    # 일치하는 항목이 있으면 "재무페이지로 이동하기" 클릭
    if found:
        finance_page_xpath = f"//*[@id='et-area']/div/div[@class='inner__area']/ul/li[{li_index}]/div/ul[@class='btn__list']/li[4]/a"
        finance_page_element = driver.find_element(By.XPATH, finance_page_xpath)
        finance_page_element.click()
        print("재무페이지로 이동 완료")
        return 1
    else:
        print("재무페이지 이동 실패")

def change_range(driver, dropdown_id="range", range_value="5", wait_time=2):

    try:
        # 드롭다운 요소 대기
        dropdown = WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((By.ID, dropdown_id))
        )

        # Select 클래스를 사용하여 범위 변경
        select = Select(dropdown)
        select.select_by_value(range_value)  # 원하는 값 선택
    
        search_button = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#etfi110m1 .btn-wrap > button"))
        )
        search_button.click()
        print(f"✅ 범위를 '{range_value}'로 성공적으로 변경했습니다.")
        return True

    except Exception as e:
        print(f"❌ 범위 변경 실패: {e}")
        return False

def get_kedcd(driver): 
    # ✅ DevTools 로그에서 네트워크 요청 가져오기
    logs = driver.get_log("performance")

    # `request.json` 요청을 추적하여 `requestId` 저장
    request_id_map = {}

    for log in logs:
        try:
            log_json = json.loads(log["message"])  
            method = log_json["message"].get("method", "")

            # 네트워크 요청이 비동기 처리되거나 fetch()로 이루어진 경우, responseReceived에서만 확인 가능
            if method == "Network.responseReceived":
                request_id = log_json["message"]["params"]["requestId"]
                request_id_map[request_id] = log_json["message"]["params"]
        except (json.JSONDecodeError, KeyError):
            continue
    # ✅ 가장 최신 requestId만 사용
    if not request_id_map:
        print("❌ `requestId`를 찾지 못했습니다.")
        driver.quit()
        exit()

    last_request_id = list(request_id_map.keys())[-1]  # ✅ 가장 마지막 requestId 선택
    print(f"✅ 선택된 `requestId`: {last_request_id}")

    # ✅ `Network.getResponseBody`로 응답 데이터 가져오기 (한 개만 실행)
    try:
        time.sleep(1)  # ✅ 요청 처리 대기 (빠른 응답 사라짐 방지)
        
        response_body = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": last_request_id})

        # ✅ 응답이 비어있는 경우 제외
        if not response_body or not response_body.get("body"):
            print(f"{last_request_id} 응답이 비어 있음")
        else:
            payload = json.loads(response_body["body"]) 

            # ✅ `kedcd` 값 추출
            kedcd = payload.get("header", {}).get("kedcd")
            if kedcd:
                print(f"✅ `kedcd` 값 찾음: {kedcd}")
                return kedcd

    except (json.JSONDecodeError, KeyError, Exception) as e:
        print(f"❌ {last_request_id} 응답 가져오기 실패: {e}")


target_tabs = {
    "재무상태표": {"accNmEng": "         Machinery and Equipment", "fsCcd": "1", "fsCls": "2"},
    "포괄손익계산서": {"accNmEng": "   Employee benefits Expenses", "fsCcd": "2", "fsCls": "1"},
    "손익계산서": {"accNmEng": "      Employee Salaries and Wages", "fsCcd": "2", "fsCls": "2"},
    "제조원가명세서": {"accNmEng": "      Salaries and Wages", "fsCcd": "5", "fsCls": "2"}
}

def get_tabs_values(driver, username, kedcd, session, years):

    headers = {
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
    'Referer': driver.current_url,
    'Origin': 'https://www.cretop.com',
    'Content-Type': 'application/json'
}
    url = 'https://www.cretop.com/httpService/request.json'

    values_list = []
    cookies = driver.get_cookies()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])

    # ✅ 탭 리스트 가져오기
    tabs = driver.find_elements(By.CSS_SELECTOR, "ul.tab-group-ul > li > a")
    existing_tabs = {tab.text.strip() for tab in tabs}

    missing_tabs = set(target_tabs.keys()) - existing_tabs
    all_tabs = set(target_tabs.keys())

    # ✅ '포괄손익계산서'가 없을 경우만 특정 탭 조정 (
    if "포괄손익계산서" in missing_tabs:
        all_tabs.discard("포괄손익계산서")
        values = ["포괄손익계산서"] +  [ None for _ in range(1, 7)]
        values_list.append(values)
    else: 
        all_tabs.discard("손익계산서")
        values = ["손익계산서"] +  [ None for _ in range(1, 7)]
        values_list.append(values)
        all_tabs.discard("제조원가명세서")
        values = ["제조원가명세서"] +  [ None for _ in range(1, 7)]
        values_list.append(values)

    for tab_name in all_tabs:
        # ✅ 해당 탭의 fsCcd, fsCls 및 accNmEng 가져오기
        tab_data = target_tabs[tab_name]
        accNmEng = tab_data["accNmEng"]
        fsCcd = tab_data["fsCcd"]
        fsCls = tab_data["fsCls"]
        if (years == 2022):
            acctDt = "20221231"
        else:
            acctDt = "20231231"

        # ✅ 요청 데이터 생성 
        data = {
            "header": {
                "trxCd": "ETFI1122R",
                "sysCd": "",
                "chlType": "02",
                "userId": username.upper(),
                "screenId": "ETFI112S2",
                "menuId": "01W0000777",
                "langCd": "ko",
                "bzno": "",
                "conoPid": "",
                "kedcd": kedcd,
                "indCd": "",
                "franMngNo": "",
                "ctrNo": "",
                "bzcCd": "",
                "infoOfrStpgeYn": "",
                "pageNum": 0,
                "pageCount": 0,
                "pndNo": ""
            },
            "ETFI1122R": {
                "kedcd": kedcd,
                "acctCcd": "Y",
                "acctDt": acctDt,
                "fsCcd": fsCcd,  
                "fsCls": fsCls,  
                "chk": "1",
                "smryYn": "N",
                "srchCls": "5"
            }
        }

        # ✅ API 요청 보내기
        response = session.post(url, json=data, headers=headers)
        response_text = response.text

        normalized_accNmEng = " ".join(tab_data["accNmEng"].split())
        pattern = fr'\{{[^}}]*"accNmEng"\s*:\s*".*?{accNmEng}.*?"[^}}]*\}}'

        matches = re.findall(pattern, response_text)

        if matches:
            for match in matches:
                match_data = json.loads(match) 
                values = [tab_name] + [years] + [match_data.get(f'val{i}') for i in range(1, 6)]
                values_list.append(values)

            print(f"✅ {tab_name} ({normalized_accNmEng}): {values_list[-1]}")
            continue

        else:
            values = [tab_name] +  [ None for _ in range(1, 7)]
            values_list.append(values)
            print(f"❌ {tab_name} 데이터를 찾을 수 없습니다.")

    return values_list if values_list else None  


chrome_options = Options()
#chrome_options.add_argument("--headless")  # UI 없이 실행하려면 추가

# 기존 사용자 데이터 디렉토리 경로 설정
user_data_dir = "/Users/ahranah/Library/Application Support/Google/Chrome"  # MacOS 사용자 데이터 디렉토리
copied_user_data_dir = "/Users/ahranah/Library/Application Support/Google/Chrome_Selenium" 

# 사용자 데이터 디렉토리 복사
if not os.path.exists(copied_user_data_dir):  # 복사본이 없을 때만 복사
    print("사용자 데이터 디렉토리 복사 중...")
    shutil.copytree(user_data_dir, copied_user_data_dir)
    print("복사 완료:", copied_user_data_dir)
# else:
#     shutil.rmtree(copied_user_data_dir)
#     shutil.copytree(user_data_dir, copied_user_data_dir) 
#     print("디렉토리 업데이트:", copied_user_data_dir)

# Selenium WebDriver 실행
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
options.add_experimental_option("detach", True) # 화면 창 닫기 방지
options.add_argument(f"user-data-dir={copied_user_data_dir}")  # 복사된 프로파일 경로 지정
options.add_argument("--profile-directory=Default")  # 특정 프로파일 중 default 사용
#options.add_argument("--headless")  # Headless 모드 활성화
options.add_argument("--disable-autofill")  # 자동완성 비활성화
options.add_experimental_option("prefs", {
    "credentials_enable_service": False,  
    "profile.password_manager_enabled": False  
})

options.add_argument("--no-sandbox")

# ✅ DevTools 로그 활성화 (네트워크 요청 추적)
options.set_capability("goog:loggingPrefs", {"performance": "ALL"})  # DevTools 네트워크 로깅 활성화

#driver 실행
service = Service(ChromeDriverManager().install())
#options.add_argument("--disable-blink-features=AutomationControlled")  # 자동화 감지 방지
driver = webdriver.Chrome(service=service, options=options)

# 사이트 이동 및 기업의 재무 페이지로 이동
site_url = "https://www.cretop.com"
driver.get(site_url)
driver.maximize_window()
driver.execute_script("document.body.style.zoom='50%'")
print("사이트 접속 완료")
driver.implicitly_wait(1.5)

# 팝업 처리 
if handle_popup(driver, popup_class="slot__right", button_text="[닫기]"):
    print("팝업 처리가 완료되었습니다.")
else:
    print("팝업 처리가 실패했습니다.")

username = "window765"  # 사용자 아이디
password = "rich1011^^"  # 비밀번호

login_to_site(driver, username, password)
    
# 로그인 확인 버튼 닫기 _ 팝업 처리 함수 
if handle_popup(driver):
    print("로그인 팝업 처리가 완료되었습니다.")
else:
    print("로그인 팝업 처리가 실패했습니다.")

time.sleep(1) 
search_key = "488-81-01678"
search_text= ""
kedcd = ""

if navigate_to_financial_page(driver, search_key):
    print(f"🚀 '{search_key}'의 재무 페이지로 성공적으로 이동했습니다.")
    time.sleep(1)

    strong_element = driver.find_element(By.XPATH, '//*[@id="etfi110m1"]/div/div[2]/div/div/div/div[2]/div/strong')
    search_text = strong_element.text.strip()
else:
    print(f"❌ '{search_key}'의 재무 페이지로 이동 실패.")


cookies = driver.get_cookies() # 로그인 상태의 세션 쿠키
session = requests.Session() # 로그인 세션 유지용(request.post()는 한 번 실행 후 세션 종료)

for cookie in cookies:
    session.cookies.set(cookie['name'], cookie['value'])
    print(f"{cookie['name']}: {cookie['value']}")

driver.execute_cdp_cmd("Network.enable", {})


kedcd = get_kedcd(driver)

value_2023 = []
value_2022 = []

value_2023 = get_tabs_values(driver, username, kedcd, session, 2023)
value_2022 = get_tabs_values(driver, username, kedcd, session, 2022)

for row, row_2022 in zip(value_2023, value_2022):
    row[1] = row_2022[2]

print (value_2023)



# # df 
# df_2023 = pd.DataFrame(value_2023, columns=["재무제표", "결산연도", "2019-12-31", "2020-12-31", "2021-12-31", "2022-12-31", "2023-12-31"])
# df_2022 = pd.DataFrame(value_2022, columns=["재무제표", "결산연도", "2018-12-31", "2019-12-31", "2020-12-31", "2021-12-31", "2022-12-31"])

# merged_df = pd.merge(df_2022, df_2023[["재무제표", "2023-12-31"]], 
#                      on=["재무제표"], how="left")

# merged_df = merged_df.drop(columns=["결산연도"])

# final_df = merged_df.apply(lambda col: col.map(lambda x:int(x) if isinstance(x, float) and not pd.isna(x) else x))


driver.quit()