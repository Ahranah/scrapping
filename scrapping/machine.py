from selenium import webdriver
import pandas as pd
import shutil
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
import time

# ChromeDriver 설정
options = webdriver.ChromeOptions()

# 기존 사용자 데이터 디렉토리 경로 설정
user_data_dir = "/Users/ahranah/Library/Application Support/Google/Chrome"  # MacOS 사용자 데이터 디렉토리
copied_user_data_dir = "/Users/ahranah/Library/Application Support/Google/Chrome_Selenium" 

# 사용자 데이터 디렉토리 복사
if not os.path.exists(copied_user_data_dir):  # 복사본이 없을 때만 복사
    print("사용자 데이터 디렉토리 복사 중...")
    shutil.copytree(user_data_dir, copied_user_data_dir)
    print("복사 완료:", copied_user_data_dir)
else:
    print("복사된 디렉토리가 이미 존재합니다:", copied_user_data_dir)

# Selenium WebDriver 실행
options = webdriver.ChromeOptions()
options.add_argument(f"user-data-dir={copied_user_data_dir}")  # 복사된 프로파일 경로 지정
options.add_argument("--profile-directory=Default")  # 특정 프로파일 중 default 사용

#driver 실행
service = Service(ChromeDriverManager().install())
#options.add_argument("--disable-blink-features=AutomationControlled")  # 자동화 감지 방지
driver = webdriver.Chrome(service=service, options=options)

try:
    # 1️⃣ 사이트 이동 및 기업의 재무 페이지로 이동
    driver.get("https://www.cretop.com")
    print("사이트 접속 완료")

    # 1️ 팝업 닫기
    try:
        # 팝업 닫기 버튼 대기 및 클릭
        close_button = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@class='btn txt-blue' and span[text()='[닫기]']]"))
        ) 
        close_button.click()
        print("팝업 닫기 완료")
    except Exception as e:
        print(f"팝업 닫기 실패 또는 팝업이 없음: {e}")

    # 2️ 로그인
    try:
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "header-login-idcr"))
        )
        login_button.click()
        # 로그인 필드 대기 및 입력
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "idModel"))
        )
        password_field = driver.find_element(By.ID, "pwModel")

        username_field.send_keys("window765")  # 여기에 사용자 아이디 입력
        password_field.send_keys("rich1011^^")  # 여기에 비밀번호 입력

        # 로그인 버튼 클릭

        login_button = driver.find_element(By.CLASS_NAME, "btn-login")  # 로그인 버튼
        login_button.click()
        print("로그인 시도 중...")

        # 로그인 성공 확인
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "user-nm"))
        )
        print("로그인 성공!")
    except Exception as e:
        print(f"로그인 실패: {e}")
    
    # 3️ 로그인 확인 버튼 닫기 // pop alert 모두 포함

    try:
        print("확인 팝업 확인 후 버튼 클릭")
        popup = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "pop-alert"))
        )
        print("팝업 확인 완료")
        
        confirm_button = popup.find_element(By.XPATH, ".//button[span[text()='확인']]")
        confirm_button.click()
        print("확인 버튼 클릭 성공")
    except Exception as e:
        print(f"팝업 확인 버튼 클릭 실패: {e}")

    # 검색어 입력 후 해당하는 기업의 재무 페이지로 이동
    try: 
        # 로그인 확인 버튼 누르고 페이지 재로딩되는 동안 검색어 입력되지 않도록 막는 작업
            # 1. 페이지 로딩 complete 후 검색어 입력 -> 이미 다 로딩된 상태에서 재로딩하는 거라 안됨
            # 2. driver.execute_script("setTimeout(() => {}, 3000);")  # 자바스크립트로 브라우저측에서 3초 대기 -> 안됨
            # 3. driver.implicitly_wait(3) # selenium이 모든 요소에 대해 대기하도록 하는 코드 -> 안됨
        time.sleep(3) #프로세스를 아예 wait으로 바꿨다가 실행
        print("3s wait")

        print("검색어 입력 시도")
        search_input = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='검색어를 입력해주세요.']"))
        )

        # 검색어 입력
        search_input.clear()  # 입력 필드 초기화
        search_key = '현진에버빌'
        search_input.send_keys(search_key)  # 검색어 입력
        print("검색어 입력 완료")

        # 검색 버튼 클릭
        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@title='검색하기']"))
        )
        search_button.click()
        print("검색 버튼 클릭 완료")

        # 추가 작업: 검색 결과 대기
        # WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located((By.CLASS_NAME, "result-class"))  # 검색 결과가 나타나는 요소
        # )
        # print("검색 결과 로드 완료")
    except Exception as e:
        print("검색 결과 로드 실패")
    
    try:
        # "key"와 동일한 기업 재무 페이지로 이동하기 위한 작업
        # key가 포함된 행 찾기
        print("검색 결과에서 대상 버튼 찾기 시도")

        keyword_row = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((
            By.XPATH, f"//div[contains(@class, 'result-txt-wrap')]/button[contains(@class, 'result-layer-open') and contains(span, '{search_key}')]")
        ))
        keyword_row.click()
        print(f" '{search_key}' 클릭 완료")

        # # 해당 div 내의 "재무" 버튼 찾기
        # financial_button = WebDriverWait(driver, 10).until(
        #     keyword_row.find_element(By.XPATH, ".//ancestor::li//ul[@class='btn__list']//a[span[text()='재무']]"))
        # financial_button.click()
        # print("재무 버튼 클릭 완료")


        # 버튼 클릭 후, 팝업 창에서 '재무 페이지로 이동하기' 클릭
        print("재무 페이지 링크 찾기 시도")

        # (선택) 팝업창과 기업명 확인
        # popup_title = WebDriverWait(driver, 10).until(
        # EC.presence_of_element_located(
        #     (By.XPATH, f"//div[contains(@class, 'info-toast-title-name')]/h3[text()='{search_key}']")))

        time.sleep(3)
        financial_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//ul[contains(@class, 'info-toast-content-btns')]/li/a[@title='재무 페이지로 이동하기']"))
            )
        
        financial_link.click()  
        print("재무 페이지 클릭 완료") 
    except Exception as e:
        print(f"재무 페이지 로드 실패: {e}")



    #재무 페이지 내부에서 작동
    # 키워드 집합
    target_tabs = {"재무상태표", "포괄손익계산서", "손익계산서", "제조원가명세서"}
    try:    
        # 1 범위를 "5년"으로 변경
        range_select = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "range"))
        )
        select = Select(range_select)
        select.select_by_value("5")  # 5년 옵션 선택
        print("범위를 5년으로 설정 완료")

        # 2 조회 버튼 클릭
        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#etfi110m1 .btn-wrap > button"))
        )
        search_button.click()
        print("조회 버튼 클릭 완료")

        # 3 {"재무상태표", "포괄손익계산서", "손익계산서", "제조원가명세서"} 있는지 확인
        try:
            
            # 1️⃣ 탭 그룹에서 모든 탭 가져오기
            tabs = driver.find_elements(By.CSS_SELECTOR, "ul.tab-group-ul > li > a")
            print(f"탭 개수: {len(tabs)}")

            for tab in tabs:
                # 탭 이름 가져오기
                tab_name = tab.text.strip()  # 탭의 텍스트 가져오기
                print(f"탭 이름: {tab_name}")

                # 2️⃣ 탭 이름이 target_tabs에 있는지 확인
                if tab_name in target_tabs:
                    print(f"탭 '{tab_name}' 확인 중...")

                     # 로딩 오버레이 사라질 때까지 대기
                    WebDriverWait(driver, 10).until(
                    EC.invisibility_of_element((By.CLASS_NAME, "vld-background"))
                    )
                    print("로딩 오버레이가 사라졌습니다.")

                    # 탭 클릭 시도
                    tab_element = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, f"//ul[@class='tab-group-ul']//a[text()='{tab_name}']"))
                    )
                    tab_element.click()
                    print(f"탭 '{tab_name}' 클릭 완료")

                    # 탭 내용 로딩 대기
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div.tabs-contents"))
                    )
                    print(f"탭 '{tab_name}' 내용 로드 완료")

                    # (1) '재무상태표' 처리
                    if tab_name == "재무상태표":
                        # nodata 확인
                        try:
                            # nodata 요소에서 텍스트 확인
                            no_data_element = driver.find_elements(By.CSS_SELECTOR, "td.nodata")
                            if no_data_element and any("조회된 자료가 없습니다." in el.text for el in no_data_element):
                                print(f"'{tab_name}' 탭: 조회된 자료가 없습니다.")
                        except Exception:
                            print("nodata 없음, 테이블 확인 시도")
                            # 기계장치 확인하는 코드 
            

                    # (2) 나머지 탭 처리
                    else:
                        try:
                        # nodata 확인
                            no_data_element = driver.find_elements(By.CLASS_NAME, "td.nodata")
                            if no_data_element and any("조회된 자료가 없습니다." in el.text for el in no_data_element):
                                print(f"'{tab_name}' 탭: 조회된 자료가 없습니다.")
                            else: 
                                print(" 테이블 확인 시도")
                                # 테이블 전체 선택
                                # 테이블 헤더 (날짜) 추출
                                attempts = 3  
                                for attempt in range(attempts):
                                    try:
                                        # Locate the table element
                                        table_element = WebDriverWait(driver, 10).until(
                                            EC.presence_of_element_located((By.CSS_SELECTOR, "div.finance-statement table"))
                                        )
                                        print("Table element found")

                                        # Extract headers
                                        header_row = table_element.find_elements(By.CSS_SELECTOR, "thead tr th span")
                                        headers = [header.text.strip() for header in header_row if header.text.strip()]
                                        print("Headers:", headers)
                                        break  # Exit loop if successful
                                    except Exception as e:
                                        print(f"col: Attempt {attempt + 1}/{attempts} failed: {e}")
                                        time.sleep(1)  # Wait before retrying
                                else: print("Failed to extract table data after multiple attempts")
                        
                                # 행 추출(매출액 등)
                                for attempt in range(attempts):
                                    try:
                                        # Wait for the table to be present
                                        row_table = WebDriverWait(driver, 10).until(
                                            EC.presence_of_element_located((By.CSS_SELECTOR, "div.finance-statement.details"))
                                        )
                                        print("Table found.")

                                        # Extract all rows with class 'depth-1'
                                        first_row = WebDriverWait(row_table, 10).until(
                                            lambda table: table.find_elements(By.CSS_SELECTOR, "tbody tr.depth-1")
                                        )

                                        # Extract data 
                                        spans = first_row.find_elements(By.CSS_SELECTOR, "td span")
                                        row_data = [span.text.strip() if span.text.strip() else 0 for span in spans]
                                        print(f"Row : {row_data}")


                                        # df 생성과 액셀 저장
                                        if row_data:
                                            df = pd.DataFrame([row_data], columns=headers)
                                            print("DataFrame created successfully.")
                                            print(df)

                                            # Save to Excel
                                            excel_filename = f"'{tab_name}'"
                                            df.to_excel(excel_filename, index=False)
                                            print(f"엑셀 저장 완료: {excel_filename}")
                                        else:
                                            print("No data found in the table.")


                                        break

                                    except Exception as e:
                                        print(f"row: Attempt {attempt + 1} failed with error: {e}")
                                        time.sleep(1)

                
                        except Exception as e:
                                print(f"테이블 데이터 추출 실패: {e}")
                    


        except Exception as e:
            print(f"탭 처리 중 오류 발생: {e}")


    except Exception as e:
        print(f"재무 페이지 내부 크롤링 실패: {e}")


finally:
    # 브라우저 닫기
    driver.quit()
