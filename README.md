# CATCHTHINGs

## Introduction

Show me your interests!

Show your intellectual abilities at CATCHTHINGs.

You can be the best in this game.

Gather your friends and play games related to your interests.


## CATCHTHINGs Summary

- 동기, 친구들과 즐길 수 있는 간단한 상식 기반 캐주얼 게임을 만들어 보고 싶다는 생각에 만들게 되었다.<br>
 
- 마침 어느정도 규모를 갖고, 1학기 프로젝트보다 업그레이드하여 객체지향의 관점에서 개발하고자 노력했다.<br>
 
- 내가 기본적인 크롤링과 게임 진행 등 서버의 Back-end를 주력으로 개발했으며, 함께한 팀원이 소켓 프로그래밍을 통해 클라이언트와 서버의 통신 및 객체 안정화를 맡아 진행했다. <br><br>


## Program Explain

- 플레이어(호스트)가 직접 카테고리 또는 관심사를 입력하면, 서버는 자동으로 인터넷의 데이터를 크롤링해 관련 단어를 선정한다. 
플레이어는 랜덤으로 선정된 단어의 사진을 보고 가장 먼저 단어를 입력하면 점수가 오르는 경쟁 방식의 게임이다. (ex. 캐치마인드) <br><br>
- 타 게임(카트라이더)의 방장이 희망하는 맵을 정해 즐기는 것과 같이 사용자가 마음대로 게임 시작 전 카테고리를 지정할 수 있다. 
카테고리에 따라 뽑아내는 데이터를 뽑아내는 것은 정해져 있지 않고, 그때그때 다르게 데이터를 가져온다.
이런 환경을 활용해 타 게임들과 차별화를 두고자 했다.


## Game Progress Flow

① 서버 프로그램 구동, 유저들의 게임 입장 및 개인정보 입력 (클라이언트 사용) <br>

② 방장(가장 먼저 들어온 유저 or 게임에서 우승한 유저)이 단어 선별 방식과 카테고리 입력 <br>

③ 각 단어 선별 방식에 따라 단어 선별 후 리스트에 저장<br>
 - 나무위키 : 키워드에 대한 나무위키 관련 정보에서 랜덤으로 단어 50가지 선정 후 검색어 API로 검색어 빈도로 유명하지 않은 단어를 걸러내어 저장<br>
 - 뉴스내용 : 키워드와 관련된 뉴스 내용을 크롤링하여 엑셀에 저장하고 konlpy를 이용해 단어를 추출, 빈도수 높은 단어 순으로 정렬 후 저장 <br>
 
④ 단어 리스트 순서를 섞고 단어와 관련된 이미지 10개를 불러와 서버에 임시로 저장 <br>

⑤ 게임이 시작되면 안내 멘트와 함께 이미지를 5초 간격으로 5개씩 2번 보여주고 유저는 사진을 바탕으로 단어 유추 <br>

⑥ 4번 ~ 5번의 단계가 반복되다가 유저 중 5점에 가장 먼저 도달하면 그 유저가 우승 <br>

⑦ 우승한 유저는 방장 권한을 얻게 되고 2번 ~ 6번 단계가 반복됨 <br>

※ 동일한 와이파이 상황만 클라이언트 접속 가능 ※



## Use Libraries
- Python 3.X
- BeautifulSoup
- Konlpy
- Request
- pandas
- Socket
