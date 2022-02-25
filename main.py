import json
import requests
import datetime

# 크롤링
from bs4 import BeautifulSoup
# 크롤링 시 페이지 로드 완료 후 가져올 수 있도록
from selenium import webdriver
# 스케쥴러
from apscheduler.schedulers.blocking import BlockingScheduler


# 주문 가능 여부 확인
def stock_check(name, url):
    chrome_driver_dir = './chromedriver'

    # 옵션 생성
    options = webdriver.ChromeOptions()
    # 창 숨기는 옵션 추가
    options.add_argument("headless")

    # 크롬 driver 실행
    driver = webdriver.Chrome(chrome_driver_dir, options=options)
    driver.implicitly_wait(10)  # 버튼이 로딩 후 변경되므로 여유있게 10초 기다리기
    driver.get(url)
    html = driver.page_source

    # 해당 url의 html문서를 soup 객체로 저장
    soup = BeautifulSoup(html, 'html.parser')
    search_result = soup.select_one(
        '#root > div > div > div.contents.product > div > div.product_view_main > form > div > div.cont.prd_select_wrap.false > div.result_btn_inner > div > ul > li.final > a')

    if search_result is not None:
        if search_result.text != "일시품절":
            kakaotalk_message_send(name, url)

    # driver 종료
    driver.quit()


# 카카오톡 메세지 보내기
def kakaotalk_message_send(name, url):

    KAKAO_TOKEN = 'TRP5EVcPMN6WkcQ4C5p98vQTyn0bN6oAhpmSbAo9cpgAAAF_Lyaz1w'
    send_url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"  # 나에게 보내기 주소

    header = {"Authorization": 'Bearer ' + KAKAO_TOKEN}

    data = {
        "template_object": json.dumps({
            "object_type": "text",
            "text": "무친 " + name + " 입고됐다고 어서 궈햇\n" + url,
            "link": {
                "web_url": url,
                "mobile_web_url": url
            },
            "button_title": "바로 확인"
        })
    }

    return requests.post(send_url, headers=header, data=data)


# 배치 목록
def batch_list():

    now = datetime.datetime.now()
    print(now)
    
    # ZV-E10
    name = 'ZV-E10'
    url = 'https://store.sony.co.kr/product-view/102263902'
    stock_check(name, url)
    
    # ZV-E10L
    name = 'ZV-E10L'
    url = 'https://store.sony.co.kr/product-view/102263904'
    stock_check(name, url)
    
    # ZV-E1
    #name = 'ZV-E1'
    #url = 'https://store.sony.co.kr/product-view/102263855'
    #stock_check(name, url)


def main():
    # 스케줄러 3분마다 실행
    repetitionTimeMinutes = 3

    sched = BlockingScheduler(timezone='Asia/Seoul')
    sched.add_job(batch_list,'interval', minutes=repetitionTimeMinutes)
    sched.start()


main()