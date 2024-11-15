
import pandas as pd
import urllib.request  #인터넷을 이용하여 데이터 요청하는 라이브러리
import matplotlib.pyplot as plt
import re
from konlpy.tag import Okt  # 한국어 불용어 처리시 사용하는 라이브러리
from tqdm import tqdm  # 프로그래스를 표시하는 라이브러리
from tensorflow.keras.preprocessing.text import Tokenizer
import numpy as np
# separate title [ 1.리뷰파일 다운로드 ] ====================
urllib.request.urlretrieve("https://raw.githubusercontent.com/e9t/nsmc/master/ratings_train.txt", filename="ratings_train.txt")
urllib.request.urlretrieve("https://raw.githubusercontent.com/e9t/nsmc/master/ratings_test.txt", filename="ratings_test.txt")

# separate title [ 2.판다스로 데이터 확인 ] ====================
train_data = pd.read_table('ratings_train.txt')
test_data = pd.read_table('ratings_test.txt')
print(train_data.info())
print(test_data.info())
# >>> 출력결과
# >>> <class 'pandas.core.frame.DataFrame'>
# >>>RangeIndex: 150000 entries, 0 to 149999
# >>> Data columns (total 3 columns):
# >>> #   Column    Non-Null Count   Dtype 
# >>> ---  ------    --------------   ----- 
# >>> 0   id        150000 non-null  int64 
# >>> 1   document  149995 non-null  object
# >>> 2   label     150000 non-null  int64 
# >>> dtypes: int64(2), object(1)
# >>> <class 'pandas.core.frame.DataFrame'>
# >>> RangeIndex: 50000 entries, 0 to 49999
# >>> Data columns (total 3 columns):
# >>> #   Column    Non-Null Count  Dtype 
# >>> ---  ------    --------------  ----- 
# >>> 0   id        50000 non-null  int64 
# >>>  1   document  49997 non-null  object
# >>> 2   label     50000 non-null  int64 
# >>> dtypes: int64(2), object(1)
# 개발자 분석내용 - document 필드의 수량이 다른 필드의 수량과 틀리므로 결측 데이터가 존재한다.

# separate title [ 3.결측데이터 수량 확인 및 제거 ] ====================
print(train_data.isna().sum())
print(test_data.isna().sum())
# ref참조
train_data = train_data.dropna(axis=0,subset="document")
test_data = test_data.dropna(axis=0,subset="document")
# 






# document 필드에서 결측치의 수량을 출력하시오
print("훈련데이터 결측수량:",train_data["document"].isna().sum())
print("테스트데이터 결측수량:",test_data["document"].isna().sum())
# 훈련데이터와 테스트데이터의 결측값을 제거한 후 결측수량을 다시 확인하시오.
train_data = train_data.dropna(axis=0,subset="document")
test_data = test_data.dropna(axis=0,subset="document")
print("훈련데이터 결측수량:",train_data["document"].isna().sum())
print("테스트데이터 결측수량:",test_data["document"].isna().sum())
# >>> 출력결과
# >>> 훈련데이터 결측수량: 5
# >>> 테스트데이터 결측수량: 3
# >>> 훈련데이터 결측수량: 0
# >>> 테스트데이터 결측수량: 0
# 개발자 분석내용 - 최초에 훈련데이터에서 5개의 결측데이터가 관측되었고,
                         테스트데이터에서 3개의 결측데이터가 관측되어
                         pandas의 dropna명령으로 제거하였다.

# separate title [ 4.중복데이터 확인 및 제거] ====================
print(train_data["document"].count())
print(train_data["document"].nunique())  #유일한 것들의 수
# >>>
# >>>
# *개발자 분석내용 - 총 데이터 수량과 유니크 데이터 수량의 차이가 있음은 중복된 데이터가 존재하고 있다는 것이다.
# 테스트데이터 또한 중복 내용이 존재하고 있으나 훈련대상 데이터가 아니지만 중복 내용을 제거하겠다.
print("훈련 중복된 데이터의 수:",
      train_data["document"].count()-train_data["document"].nunique())
print(test_data["document"].count())
print(test_data["document"].nunique())
print("테스트 중복된 데이터의 수:",
      test_data["document"].count()-test_data["document"].nunique())
# *개발자 분석내용 - 테스트 데이터 또한 중복 내용이 존재하고 있으나, 훈련 대상 데이터가 아니지만 중복데이터 제거를 하지 않겠다.

#ref 참조 DataFrame.drop_duplicates(subset=None
train_data=train_data.drop_duplicates(subset="document")  # 훈련데이터 중복된 데이터 제거
test_data=test_data.drop_duplicates(subset="document")    # 테스트데이터 중복된 데이터 제거
print("훈련 중복된 데이터의 수:",
      train_data["document"].count()-train_data["document"].nunique())
print("테스트 중복된 데이터의 수:",
      test_data["document"].count()-test_data["document"].nunique())
# >>> 훈련 중복된 데이터의 수: 0
# >>> 테스트 중복된 데이터의 수: 0
# *개발자 분석내용 - 모든 데이터의 중복이 제거되어 중복데이터 수가 0으로 표기되었다.

# separate title [ 5.한글을 제외한 문자 제거와 형태소별로 분류 ] ========================
print(train_data[0:5])
         id                                           document  label
0   9976970                                  아 더빙 진짜 짜증나네요 목소리      0
1   3819312                         흠포스터보고 초딩영화줄오버연기조차 가볍지 않구나      1
2  10265843                                  너무재밓었다그래서보는것을추천한다      0
3   9045019                          교도소 이야기구먼 솔직히 재미는 없다평점 조정      0
4   6483659  사이몬페그의 익살스런 연기가 돋보였던 영화스파이더맨에서 늙어보이기만 했던 커스틴 던...      1
# *개발자 분석내용 - ...? 영문 등은 감성분석에 불필요하므로 제거대상이다.
# 정규표현식을 이용한 한글과 공백을 제외한 모든 단어는 제거
train_data["document"] = \
    train_data["document"].replace(r"[^\sㄱ-ㅎㅏ-ㅣ가-힣]","",regex=True) 


test_data["document"] = \
    test_data["document"].replace(r"[^\sㄱ-ㅎㅏ-ㅣ가-힣]","",regex=True) 


