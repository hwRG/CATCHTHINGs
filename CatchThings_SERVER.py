# -*- coding:utf-8 -*-
# -*-coding: utf-8-*-
import xml.etree.ElementTree as ET
from urllib.request import urlopen
from collections import Counter
from bs4 import BeautifulSoup
from datetime import datetime
from random import shuffle
from konlpy.tag import Okt
from queue import Queue
import urllib.request
import pandas as pd
import requests
import json
import random
import time
import cv2
import socket
import socketserver
import threading

HOST = ''
PORT = 8080
lock = threading.Lock()
q = Queue()
Answer = ''
s1_check = '' #시작
s2_check = '' #검색방법
s3_check = '' #카테고리


# 연예인, 배우 관련 내용은 네이버 TV연예 카테고리인 관계로 크롤링 불가능
class naver_news_Crawling:

    # 뉴스 크롤링 준비
    def __init__(self, gameman, user_category):
        self.gameman = gameman
        self.csv_outputFileName = ''
        self.news_contents = []
        self.result_path = 'CrawlingData/'
        self.now = datetime.now()

        # 최대 페이지 수, 시작, 끝 날짜 정해야 함
        self.maxpage = 5
        self.query = user_category
        self.start_date = '2019.08.01'
        self.end_date = '2019.10.01'

        self.okt = Okt()
        self.news_Crawling = []
        self.word_collection = []
        self.word_list = []
        self.sorted_word_list = []

    def get_news(self, n_url):
        request = requests.get(n_url)
        soup = BeautifulSoup(request.content, 'html.parser')

        title = soup.select('h3#articleTitle')[0].text
        self.news_contents.append(title)

        date = soup.select('.t11')[0].get_text()[:11]
        self.news_contents.append(date)

        _text = soup.select('#articleBodyContents')[0].get_text().replace('\n', " ")
        text = _text.replace("// flash 오류를 우회하기 위한 함수 추가 function _flash_removeCallback() {}", "")

        self.news_contents.append(text.strip())
        self.news_contents.append(n_url)
        company = soup.select('#footer address')[0].a.get_text()
        self.news_contents.append(company)

        return self.news_contents

    # 지정한 키워드를 바탕으로 네이버 뉴스 크롤링 하는 함수
    def crawler(self):
        s_from = self.start_date.replace(".", "")
        e_to = self.end_date.replace(".", "")
        page = 1
        self.maxpage = (int(self.maxpage) - 1) * 10 + 1  # 11= 2페이지 21=3페이지 31=4페이지 등

        # 크롤링 한 내용 Contents_text 에 임시 저장
        f = open("CrawlingData/contents_text.txt", 'w', encoding='utf-8')

        while page < self.maxpage:
            print(page)
            url = "https://search.naver.com/search.naver?where=news&query=" + \
                  self.query + "&sort=0&photo=3&ds=" + self.start_date + "&de=" + self.end_date + \
                  "&nso=so%3Ar%2Cp%3Afrom" + s_from + "to" + e_to + "%2Ca%3A&start=" + str(page)
            req = requests.get(url)
            print(url)
            cont = req.content
            soup = BeautifulSoup(cont, 'html.parser')

            for urls in soup.select("._sp_each_url"):
                try:
                    # print(urls["href"]) <- 잡다한 주소 포함 확인
                    if urls["href"].startswith("https://news.naver.com"):
                        # print(urls["href"]) <- 주소 확인
                        news_detail = self.get_news(urls["href"])

                        # date, company, title, text 파일에 내용 작성
                        f.write("{}\t{}\t{}\t{}\t{}\n".format(news_detail[1], news_detail[4], news_detail[0],
                                                              news_detail[2], news_detail[3]))  # new style
                except Exception as e:
                    print(e)
                    continue
            page += 10
        f.close()

    # Contents_text에 임시 보관한 데이터 엑셀에 삽입하는 함수
    def excel_make(self):
        data = pd.read_csv(self.result_path + 'contents_text.txt', sep='\t', header=None, error_bad_lines=False)
        data.columns = ['years', 'company', 'title', 'contents', 'link']
        print(data)

        csv_outputFileName = '%s-%s-%s %s시 %s분 {} 관련 신문 {} ~ {}.csv'.format(self.query, self.start_date,
                                                                            self.end_date) % (
                                 self.now.year, self.now.month, self.now.day, self.now.hour, self.now.minute)
        data.to_csv(self.result_path + csv_outputFileName, encoding='utf-8-sig')
        return csv_outputFileName

    # Konlpy로 빈도수 계산
    def csvKonlpy(self):
        with open(self.result_path + self.csv_outputFileName, "r", encoding='UTF-8') as nationWide_Population_f:
            for lineContent in nationWide_Population_f:
                self.news_Crawling.append(lineContent.strip('\n').split(','))
        okt = Okt()
        for i in range(len(self.news_Crawling) - 1):
            self.word_collection.append(okt.nouns(self.news_Crawling[i + 1][4]))
        print(self.word_collection)
        for i in range(len(self.word_collection)):
            for j in range(len(self.word_collection[i])):
                self.word_list.append(self.word_collection[i][j])

        count = Counter(self.word_list)
        tag_count = []
        tags = []
        for n, c in count.most_common(100):
            dics = {'tag': n, 'count': c}
            if len(dics['tag']) >= 2 and len(tags) <= 49:
                tag_count.append(dics)
                tags.append(dics['tag'])
        sorted_word_list = []
        for tag in tag_count:
            print("{:<14}".format(tag['tag']), end='\t')
            sorted_word_list.append(tag['tag'])
            print("{}".format(tag['count']))
        # print(sorted_word_list)
        return sorted_word_list

    def main(self):
        self.crawler()
        self.csv_outputFileName = self.excel_make()
        self.sorted_word_list = self.csvKonlpy()
        print(self.sorted_word_list)
        return self.sorted_word_list


class namu_Crawling:
    def __init__(self, gameman):
        super().__init__()
        self.gameman = gameman

        self.user_category = ''
        self.real_category = ''
        self.resp = ''
        self.html = ''

        self.select_target_method = ''
        self.target_bundle = []
        self.sorted_target_bundle = []

    def new_thread(self):
        return game(self.gameman, parent=self)

    def go_word_check(self):
        self.select_category()
        if self.user_category == '유행어':
            self.user_category = '속어 유행어 관련 정보'
        elif self.user_category == '배우':
            self.user_category = '배우/한국'
        elif self.user_category == '개그맨':
            self.user_category = '코미디언/목록'

        self.resp = requests.get('https://namu.wiki/w/' + self.user_category)
        self.html = self.resp.text

    # elif self.select_target_method == '뉴스내용':
    # namu_Crawling.__init__(self, self.user_category, self.real_category, self.soup)
    # naver_news_Crawling.__init__(self, self.user_category)
    # self.final_target_bundle = self.sorted_word_list
    # self.final_target_bundle = self.parent.ready()

    # 카테고리 설정하는 함수
    def select_category(self):
        global s1_check
        global s2_check
        global s3_check

        self.gameman.messageHandler('*', '시작을 입력하시면 10초 뒤 게임 시작')
        s1_check = ''
        while 1:
            if s1_check == '(시작)':
                break
        self.gameman.messageHandler('*', '10초뒤 게임 시작합니다\n')
        time.sleep(10)

        self.gameman.messageHandler('*', "CatchThingS에 오신 것을 환영합니다!\n")
        self.gameman.messageHandler('*', "     / 검색 방법 종류 / \n")
        self.gameman.messageHandler('*', "     1.  나무위키 \n")
        self.gameman.messageHandler('*', "     2.  뉴스내용 \n")
        self.gameman.messageHandler('*', "검색 방법 종류를 선택해주세요\n")
        s2_check = ''
        while 1:
            if s2_check == '(나무위키)':
                self.gameman.messageHandler('*', "검색방법 1번 나무위키를 선택하셨습니다\n")
                self.select_target_method = '나무위키'  # input("게임 단어 선택 방식을 입력해 주세요 : ")
                break
            elif s2_check == '(뉴스)':
                self.gameman.messageHandler('*', "검색방법 2번 뉴스내용을 선택하셨습니다\n")
                self.select_target_method = '뉴스내용'
                break

        self.gameman.messageHandler('*', "     /   카테고리   / \n")
        self.gameman.messageHandler('*', "     1.  유행어 \n")
        self.gameman.messageHandler('*', "     2.  배우 \n")
        self.gameman.messageHandler('*', "     3.  개그맨 \n")
        self.gameman.messageHandler('*', "희망하는 카테고리를 선택하세요 : ")
        s3_check = ''
        while 1:
            if s3_check == '(유행어)':
                self.gameman.messageHandler('*', "카테고리 1번 유행어를 선택하셨습니다\n")
                self.user_category = '유행어'
                break
            elif s3_check == '(배우)':
                self.gameman.messageHandler('*', "카테고리 2번 배우를 선택하셨습니다\n")
                self.user_category = '배우'
                break
            elif s3_check == '(개그맨)':
                self.gameman.messageHandler('*', "카테고리 3번 개그맨을 선택하셨습니다\n")
                self.user_category = '개그맨'
                break


        #self.user_category = '배우'  # input("희망하는 카테고리를 선택하세요 : ")
        self.real_category = self.user_category
        print("")

    # 랜덤으로 ~개 단어 선택하는 함수
    def random_select_target(self):
        target_bundle = []
        cur_title = []
        soup = BeautifulSoup(self.html, 'html.parser')
        for i in range(50):
            # a태그의 class형 wiki-link-internal 라는 이름을 가진 것들 뽑아옴
            for a in soup('a'):
                if 'class' in a.attrs and 'wiki-link-internal' in a['class']:
                    cur_title.append(a.get_text())
            target = random.choice(cur_title)
            target_bundle.append(target)
        self.gameman.messageHandler('*', '%s %s\n' % (self.real_category, "총 50개 단어가 선택되었습니다."))
        return target_bundle

    # 유명한 정도를 측정하여 50개 중, 인기 없는 단어 걸러내는 함수
    def how_awareness(self, target_bundle):
        # hVyhVr7A2gqOPVuXq15f / CtlRI_PPk1
        # C65HLqyMcLzZLivN49pn / 8w9i32Byen
        # dop45eQ_ymP6C3qICsmh / t6GZPBxYBz
        url = "https://openapi.naver.com/v1/datalab/search"
        client_id = "hVyhVr7A2gqOPVuXq15f"
        client_secret = "CtlRI_PPk1"
        # yesterday = str(datetime.today().year) + "-" + str(datetime.today().month) + "-" + str(datetime.today().day - 1)
        # beforeYesterday = str(datetime.today().year) + "-" + str(datetime.today().month) + "-" + str(datetime.today().day - 2)

        sorted_target_bundle = []
        count_target_bundle = len(target_bundle)

        self.gameman.messageHandler('*', "단어 걸러내는 중\n")
        for i in range(count_target_bundle):
            body_dict = {"startDate": "2019-11-01",
                         "endDate": "2019-11-10",
                         "timeUnit": "date",
                         "ages": ["1"],
                         "keywordGroups": [{"groupName": target_bundle[i], "keywords": [target_bundle[i]]}]}

            body = json.dumps(body_dict, ensure_ascii=False)

            request = urllib.request.Request(url)
            request.add_header("X-Naver-Client-Id", client_id)
            request.add_header("X-Naver-Client-Secret", client_secret)
            request.add_header("Content-Type", "application/json")
            response = urllib.request.urlopen(request, data=body.encode("utf-8"))

            individual = json.loads(response.read().decode('utf-8'))

            ratio = [each['ratio'] for each in individual['results'][0]['data']]
            date = [each['period'] for each in individual['results'][0]['data']]
            awareness = 0
            ratio_count = len(ratio)
            if ratio_count > 8:
                sorted_target_bundle.append(target_bundle[i])
        self.gameman.messageHandler('*', '%s\n' % ("총 " + str(len(sorted_target_bundle)) + "개의 단어가 선택되었습니다!"))
        return sorted_target_bundle

    def ready(self):
        self.go_word_check()
        if self.select_target_method == '나무위키':
            self.target_bundle = self.random_select_target()
            self.sorted_target_bundle = self.how_awareness(self.target_bundle)
        elif self.select_target_method == '뉴스내용':
            news = naver_news_Crawling(self.gameman, self.real_category)
            self.sorted_target_bundle = news.main()
        print('a')
        return self.sorted_target_bundle



class game(threading.Thread):
    def __init__(self, gameman, parent=None):
        super(game, self).__init__()
        self.parent = parent
        self.gameman = gameman

        self.ID = dict()
        self.user_category = ''
        self.real_category = ''
        self.select_target_method = ''
        self.final_target_bundle = ''

    def run(self):
        while True:
            self.final_target_bundle = self.parent.ready()
            print(self.final_target_bundle)
            shuffle(self.final_target_bundle)

            self.start_game()
            self.gameman.messageHandler('*', "%s\n" % "게임 종료")

    # 선정된 단어의 사진을 랜덤하게 불러오는 함수
    def random_search(self, target):
        # d_nAX8q9ZlnFPsBrdCH4 / 74H1ih489L
        # C65HLqyMcLzZLivN49pn / 8w9i32Byen
        client_id = "d_nAX8q9ZlnFPsBrdCH4"
        client_secret = "74H1ih489L"
        encText = urllib.parse.quote(target)
        enctText = urllib.parse.quote(self.user_category)
        url = "https://openapi.naver.com/v1/search/image.xml?query=" + encText
        display = '&display=25'
        start = '&start=1'
        sort = '&sort=sim'
        filter = '&filter=large'
        url += (display + start + sort + filter)

        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", client_id)
        request.add_header("X-Naver-Client-Secret", client_secret)
        time.sleep(0.1)
        self.gameman.messageHandler('*', "사진 랜덤 업로드 중\n")
        tree = ET.ElementTree(file=urlopen(request))
        root = tree.getroot()
        count = 1
        for data in root.iter("item"):
            if count > 10:
                break
            try:
                urllib.request.urlretrieve(data.findtext('link'), str(count) + '.jpg')
                count += 1
            except:
                pass
        self.gameman.messageHandler('*', "사진 랜덤 업로드 완료\n")

    # 10개로 선택된 사진 중 앞 5개를 2초간 보여주는 함수
    def show_first_images(self):
        #cv2.namedWindow("Select First Images", cv2.WINDOW_NORMAL)
        #cv2.moveWindow("Select First Images", 0, 0)
        #cv2.resizeWindow("Select First Images", 1500, 500)

        image1 = '1.jpg'
        image2 = '2.jpg'
        image3 = '3.jpg'
        image4 = '4.jpg'
        image5 = '5.jpg'
        img1 = cv2.imread(image1, 1);
        img2 = cv2.imread(image2, 1);
        img3 = cv2.imread(image3, 1);
        img4 = cv2.imread(image4, 1);
        img5 = cv2.imread(image5, 1);
        img1 = cv2.resize(img1, (1200, 500))
        img2 = cv2.resize(img2, (1200, 500))
        img3 = cv2.resize(img3, (1200, 500))
        img4 = cv2.resize(img4, (1200, 500))
        img5 = cv2.resize(img5, (1200, 500))

        first = cv2.hconcat([img1, img2, img3, img4, img5])
        cv2.imwrite('0.jpg', first)
        #cv2.imshow('Select First Images', first)
        #cv2.waitKey(2000)
        #cv2.destroyAllWindows()

    # 10개로 선택된 사진 중 뒤 5개를 2초간 보여주는 함수
    def show_second_images(self):
        #cv2.namedWindow("Select Second Images", cv2.WINDOW_NORMAL)
        #cv2.moveWindow("Select Second Images", 0, 0)
        #cv2.resizeWindow("Select Second Images", 1500, 500)
        image6 = '6.jpg'
        image7 = '7.jpg'
        image8 = '8.jpg'
        image9 = '9.jpg'
        image10 = '10.jpg'
        img6 = cv2.imread(image6, 1);
        img7 = cv2.imread(image7, 1);
        img8 = cv2.imread(image8, 1);
        img9 = cv2.imread(image9, 1);
        img10 = cv2.imread(image10, 1);
        img6 = cv2.resize(img6, (1200, 500))
        img7 = cv2.resize(img7, (1200, 500))
        img8 = cv2.resize(img8, (1200, 500))
        img9 = cv2.resize(img9, (1200, 500))
        img10 = cv2.resize(img10, (1200, 500))
        second = cv2.hconcat([img6, img7, img8, img9, img10])
        cv2.imwrite('0.jpg', second)
        #cv2.imshow('Select Second Images', second)
        #cv2.waitKey(2000)
        #cv2.destroyAllWindows()

    # 게임 진행을 위한 함수
    def image_game(self, target):
        global Answer
        userWrong = 0  # 틀린 개수에 따라 오답이 진행 됨
        while True:
            eve = threading.Event()
            if userWrong == 0:
                self.show_first_images()
                self.gameman.messageHandler('*', "%s" % "transmit_picture")
                self.gameman.messageHandler('*', "%s\n" % ("힌트 : " + str(len(target)) + "자"))
            elif userWrong == 1:
                self.gameman.messageHandler('*', "%s\n" % ("앞 글자 : " + target[0]))
                self.show_second_images()
                self.gameman.messageHandler('*', "%s" % "사진_전송")
            elif userWrong == 2:
                self.gameman.messageHandler('*', "%s\n" % ("뒷 글자 : " + target[len(target) - 1]))
            else:
                self.gameman.messageHandler('*', "대기시간이 초과되었습니다. \n")
                self.gameman.messageHandler('*', "유감스럽습니다.\n")
                self.gameman.messageHandler('*', '%s\n' % ("정답은 " + target + "입니다."))
                return 0

            Answer = target
            self.gameman.messageHandler('*', "[대기시간 20초]\n")
            self.gameman.messageHandler('*', "사진의 정답을 입력해 주세요 : \n")

            q.put(eve)
            eve.wait(timeout=20)

            if Answer == '':
                return 1

            self.gameman.messageHandler('*', "대기시간이 초과되었습니다. \n")
            self.gameman.messageHandler('*', "힌트가 제공됩니다. \n")
            userWrong += 1

    # 게임 시작을 위한 메인 함수
    def start_game(self):
        # 여기부터 sorted_target_bundle을 각 클라이언트에 보급하고 게임 진행하면 될 듯
        userCount = 0
        self.ID["한우람쥐"] = 0

        # 최종 선택된 내용을 바탕으로 게임 시작

        for i in range(len(self.final_target_bundle)):
            time.sleep(0.5)
            print("")
            self.gameman.messageHandler('*', '%d%s\n' % (i + 1, "번째 게임을 시작합니다"))
            self.random_search(self.final_target_bundle[i])
            userPlus = self.image_game(self.final_target_bundle[i])
            self.ID["한우람쥐"] += userPlus
            print("")
            print(list(self.ID.keys())[0], " 님의 현재 점수는 ", self.ID["한우람쥐"], "점 입니다.")


class UserManager:
    def __init__(self):
        self.users = {}

    def addUser(self, username, conn, addr):
        if username in self.users:
            conn.send('Already registered user.\n'.encode('utf-8'))
            return None

        lock.acquire()
        self.users[username] = (conn, addr)
        lock.release()

        self.sendMessageToAll('[%s is Coming]' % username)
        print('+++ Count Members [%d]' % len(self.users))

        return username

    def removeUser(self, username):
        if username not in self.users:
            return

        lock.acquire()
        del self.users[username]
        lock.release()

        self.sendMessageToAll('[%s is Leaving]' % username)
        print('--- Count Members [%d]' % len(self.users))

    def messageHandler(self, username, msg):
        global Answer
        global s1_check
        global s2_check
        global s3_check

        if msg[0] != '/':
            self.sendMessageToAll('[%s] %s' % (username, msg))
            if Answer != '' and Answer == msg:
                eve = q.get()
                self.sendMessageToAll('[*] %s님 정답입니다!' % username)
                Answer = ''
                eve.set()

            if msg.find('(시작)') != -1:
                s1_check = '(시작)'
            elif msg.find('(나무위키') != -1:
                s2_check = '(나무위키)'
            elif msg.find('(뉴스)') != -1:
                s2_check = '(뉴스)'
            elif msg.find('(유행어)') != -1:
                s3_check = '(유행어)'
            elif msg.find('(배우)') != -1:
                s3_check = '(배우)'
            elif msg.find('(개그맨)') != -1:
                s3_check = '(개그맨)'

            return

        if msg.strip() == '/quit':
            self.removeUser(username)
            return -1

    def sendMessageToAll(self, msg):
        for conn, addr in self.users.values():
            conn.send(msg.encode('utf-8'))


class MyTcpHandler(socketserver.BaseRequestHandler):
    userman = UserManager()
    game_sc = namu_Crawling(userman)
    #news_sc = naver_news_Crawling(userman, '')
    thread = game_sc.new_thread()
    thread.start()

    def handle(self):
        print('[%s] Connected' % self.client_address[0])

        try:
            username = self.registerUsername()
            msg = self.request.recv(1024)
            while msg:
                print('[%s] %s' % (username, msg.decode('utf-8')))
                if self.userman.messageHandler(username, msg.decode('utf-8')) == -1:
                    self.request.close()
                    break
                msg = self.request.recv(1024)

        except Exception as e:
            print(e)

        print('[%s] Disconnect' % self.client_address[0])
        self.userman.removeUser(username)

    def registerUsername(self):
        while True:
            self.request.send('Login ID: '.encode('utf-8').strip())
            username = self.request.recv(1024)
            username = username.decode('utf-8').strip()
            if self.userman.addUser(username, self.request, self.client_address):
                return username


class ChatingServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


def runServer():
    global Answer
    global Check
    print('[ Start Chating Server ]')
    print('[ Quit : Ctrl-C ]')

    try:
        server = ChatingServer((HOST, PORT), MyTcpHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print('[ Shut down Chat Server ]')
        server.shutdown()
        server.server_close()


runServer()
