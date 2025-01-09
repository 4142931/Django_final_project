import json
import os
import sqlite3
from collections import defaultdict
import re

import networkx as nx
import pandas as pd
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required

from news_analyzer.daily_analysis import preprocess_text
from news_analyzer.daily_analysis.wordcloud import extract_keywords
from news_analyzer.database import fetch_news_data
from .models import Question, InvestmentResult
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from datetime import datetime, timedelta


# 메인 페이지
def index_view(request):
    return render(request, 'survey/index.html')



# 로그인 & 로그아웃
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # 회원가입 후 자동 로그인 처리
            return redirect('News_home')  # 홈 페이지로 리디렉션
    else:
        form = UserCreationForm()
    return render(request, 'survey/signup.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('News_home')




# 마이페이지
def mypage_view(request):
    # 사용자의 가장 최신 결과 가져오기
    latest_result = InvestmentResult.objects.filter(user_id=request.user.id).order_by('-id').first()

    # 결과 유형 결정
    if latest_result:
        user_mbti_type = latest_result.result_type
    else:
        user_mbti_type = "결과 없음"

    # 공통 데이터에서 결과 가져오기
    results = get_mbti_data()
    user_result = results.get(user_mbti_type, {
        "mbti_type": "금융 성향 테스트를 진행해보세요",
        "mbti_description": "결과가 없습니다",
        "detailed_description01": "",
        "image_path": "survey/images/person.jpg",
    })

    # 추가 데이터를 마이페이지에 전달
    stock_list = [
        {'name': '삼성전자', 'price': '71,500원', 'description': '전자 제품 대기업'},
        {'name': '카카오', 'price': '123,000원', 'description': 'IT 플랫폼 기업'},
    ]

    context = {
        'mbti_type': user_result['mbti_type'],
        'mbti_description': user_result.get('mbti_description', '기본 설명이 준비되지 않았습니다.'),
        'detailed_description01': user_result['detailed_description01'],
        'image_path': user_result.get('image_path', 'survey/images/person.jpg'),
        'stock_list': stock_list,
    }

    return render(request, 'survey/mypage.html', context)





# 주식 추천
@login_required
def stock_recommendations(request):
    return render(request, 'survey/stock_recommendations.html')




# News
def News_home(request):
    news_data = fetch_news_data()
    recent_news = []

    # 최신 뉴스 (5개)
    for title, content, url in news_data[:5]:
        recent_news.append({
            'title': title,
            'url': url,
        })

    # 뉴스 카테고리 정의
    categories = {
        '금융': r'금융|은행|저축|대출|이자',
        '증권': r'증권|주식|코스피|코스닥|채권',
        '부동산': r'부동산|아파트|주택|전세|월세',
        '경제 일반': r'경제|산업|무역|수출|기업'
    }

    categorized_news = defaultdict(list)

    # 뉴스 데이터를 카테고리별로 분류
    for title, content, url in news_data:
        categorized = False
        for category, pattern in categories.items():
            if re.search(pattern, title) or re.search(pattern, content):
                if len(categorized_news[category]) < 4:
                    categorized_news[category].append({
                        'title': title,
                        'url': url  # URL 추가
                    })
                    categorized = True
                    break

        # 분류되지 않은 뉴스는 '경제 일반'에 추가
        if not categorized and len(categorized_news['경제 일반']) < 4:
            categorized_news['경제 일반'].append({
                'title': title,
                'url': url  # URL 추가
            })

    # 핫키워드 추출
    word_count = defaultdict(int)
    for title, content, url in news_data:
        words = re.findall(r'\w+', title)
        for word in words:
            if len(word) >= 2:  # 2글자 이상의 단어만 카운트
                word_count[word] += 1

    # 가장 많이 등장한 5개 단어를 핫키워드로 선정
    keywords = sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:5]
    hot_keywords = [keyword for keyword, _ in keywords]

    # 컨텍스트 생성 및 렌더링
    context = {
        'recent_news': recent_news,
        'categorized_news': dict(categorized_news),
        'hot_keywords': hot_keywords,
    }
    return render(request, 'survey/News_home.html', context)


@login_required
def hot_topic(request):
    try:
        conn = sqlite3.connect("news_analyzer/inbest.db")
        cursor = conn.cursor()

        cursor.execute("""
           SELECT title, content 
           FROM news 
           ORDER BY date DESC 
           LIMIT 50
       """)

        news_data = cursor.fetchall()

        # 감성어 사전 로드
        base_path = os.path.join(os.path.dirname(__file__), '..', 'news_analyzer', 'csv')
        senti_lex = pd.read_csv(os.path.join(base_path, 'SentiWord_Dict.csv'))
        positive_words = set(senti_lex[senti_lex['polarity'] > 0]['word'])
        negative_words = set(senti_lex[senti_lex['polarity'] < 0]['word'])

        positive_news = []
        negative_news = []
        main_positive_news = None
        main_negative_news = None

        # 뉴스 분류
        for title, content in news_data:
            words = set(re.findall(r'[가-힣]+', title))
            pos_score = len(words & positive_words)
            neg_score = len(words & negative_words)

            news_item = {
                'title': title,
                'content': content
            }

            if pos_score > neg_score:
                if not main_positive_news:  # 첫 번째 긍정 뉴스를 메인 뉴스로
                    main_positive_news = news_item
                elif len(positive_news) < 4:  # 나머지는 목록에
                    positive_news.append(news_item)
            elif neg_score > pos_score:
                if not main_negative_news:  # 첫 번째 부정 뉴스를 메인 뉴스로
                    main_negative_news = news_item
                elif len(negative_news) < 4:  # 나머지는 목록에
                    negative_news.append(news_item)

        # 부족한 기사 채우기
        if not main_positive_news:
            main_positive_news = {
                'title': '오늘은 주요 호재가 없습니다',
                'content': '현재 시장에 주요한 호재성 뉴스가 없습니다.'
            }
        if not main_negative_news:
            main_negative_news = {
                'title': '오늘은 주요 악재가 없습니다',
                'content': '현재 시장에 주요한 악재성 뉴스가 없습니다.'
            }

        while len(positive_news) < 4:
            positive_news.append({
                'title': '',
                'content': '추가 호재 기사가 없습니다.'
            })
        while len(negative_news) < 4:
            negative_news.append({
                'title': '',
                'content': '추가 악재 기사가 없습니다.'
            })

        context = {
            'main_positive_news': main_positive_news,
            'main_negative_news': main_negative_news,
            'positive_news': positive_news,
            'negative_news': negative_news,
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        default_item = {
            'title': '데이터를 불러올 수 없습니다.',
            'content': '내용을 불러올 수 없습니다.'
        }
        context = {
            'main_positive_news': default_item,
            'main_negative_news': default_item,
            'positive_news': [default_item] * 4,
            'negative_news': [default_item] * 4
        }

    finally:
        if 'conn' in locals():
            conn.close()

    return render(request, 'survey/hot_topic.html', context)


@login_required
def daily_analysis(request):
    def convert_kr_date(date_str):
        try:
            # 마침표 제거 및 분리
            parts = date_str.replace('.', '').split()

            # 날짜 부분 처리
            date_nums = parts[0].split()
            year = int(date_nums[0][:4])
            month = int(date_nums[0][4:6])
            day = int(date_nums[0][6:8])

            # 시간 부분 처리
            time_parts = parts[2].split(':')
            hour = int(time_parts[0])
            minute = int(time_parts[1])

            # 오전/오후 처리
            if parts[1] == '오후' and hour < 12:
                hour += 12
            elif parts[1] == '오전' and hour == 12:
                hour = 0

            return datetime(year, month, day, hour, minute).date()
        except Exception as e:
            print(f"Date conversion error for {date_str}: {str(e)}")
            # 오류 발생 시 현재 날짜 반환
            return datetime.now().date()

    try:
        # inbest.db 연결
        db_path = os.path.join("news_analyzer", "inbest.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 7일간의 뉴스 데이터 조회
        cursor.execute("""
            SELECT title, content, author, date 
            FROM news 
            WHERE date >= datetime('now', '-7 day')
            ORDER BY date DESC;
        """)

        news_data = cursor.fetchall()
        print(f"Total news data fetched: {len(news_data)}")

        if news_data:
            # 데이터프레임 생성
            df = pd.DataFrame(news_data, columns=['title', 'content', 'author', 'date'])

            # 날짜 변환
            df['date'] = df['date'].apply(convert_kr_date)

            print(f"DataFrame shape: {df.shape}")

            # 워드클라우드 데이터 생성
            cloud_data = extract_keywords(df[['title', 'content', 'author']].values.tolist())
            print(f"Word cloud data length: {len(cloud_data)}")

            # 카테고리 정의
            categories = {
                '경제': ['금리', '주식', 'GDP', '물가', '경기', '원화'],
                '투자': ['ETF', '채권', '펀드', '배당', '투자', '수익'],
                '기업': ['실적', '공시', '매출', '영업이익', '기업', '성장'],
                '정책': ['정부', '규제', '정책', '법안', '제도', '당국']
            }

            # 네트워크 데이터 생성
            network_data = {
                'nodes': [{'id': 'center', 'label': '키워드', 'category': 'center'}],
                'edges': []
            }

            # 워드클라우드 데이터에서 나온 단어들을 기준으로 카테고리 매핑
            word_set = set(item['text'] for item in cloud_data)

            # 카테고리별 키워드 추가
            for category, keywords in categories.items():
                matching_keywords = [word for word in keywords if word in word_set]
                if matching_keywords:
                    network_data['nodes'].append({
                        'id': category,
                        'label': category,
                        'category': 'main'
                    })
                    network_data['edges'].append({
                        'source': 'center',
                        'target': category,
                        'weight': 3
                    })

                    for word in matching_keywords:
                        network_data['nodes'].append({
                            'id': word,
                            'label': word,
                            'category': 'keyword'
                        })
                        network_data['edges'].append({
                            'source': category,
                            'target': word,
                            'weight': 2
                        })

            print(f"Network data nodes: {len(network_data['nodes'])}, edges: {len(network_data['edges'])}")

            # 언론사별 일간 보도 현황
            press_daily = df.groupby(['date', 'author']).size().unstack(fill_value=0)

            # 상위 7개 언론사 선택
            top_authors = df['author'].value_counts().nlargest(7).index
            press_daily = press_daily[top_authors]

            press_data = {
                'dates': [d.strftime('%Y-%m-%d') for d in press_daily.index],
                'authors': list(press_daily.columns),
                'values': press_daily.values.tolist()
            }

            print(f"Press data dates: {len(press_data['dates'])}, authors: {len(press_data['authors'])}")

            context = {
                'wordcloud_data': json.dumps(cloud_data, ensure_ascii=False),
                'network_data': json.dumps(network_data, ensure_ascii=False),
                'press_data': json.dumps(press_data, ensure_ascii=False),
                'analysis_date': datetime.now().strftime('%Y.%m.%d %H:%M')
            }
        else:
            context = {
                'wordcloud_data': json.dumps([{"text": "데이터 없음", "size": 50, "sentiment": "neutral"}]),
                'network_data': json.dumps({'nodes': [], 'edges': []}),
                'press_data': json.dumps({'dates': [], 'authors': [], 'values': []}),
                'analysis_date': datetime.now().strftime('%Y.%m.%d %H:%M')
            }

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        context = {
            'wordcloud_data': json.dumps([{"text": "오류 발생", "size": 50, "sentiment": "neutral"}]),
            'network_data': json.dumps({'nodes': [], 'edges': []}),
            'press_data': json.dumps({'dates': [], 'authors': [], 'values': []}),
            'analysis_date': datetime.now().strftime('%Y.%m.%d %H:%M')
        }

    finally:
        if 'conn' in locals():
            conn.close()

    return render(request, 'survey/daily_analysis.html', context)


# 금융성향테스트
def get_mbti_data():
    return {
        "사자": {
            "mbti_type": "사자",
            "mbti_description": "하이 리스크에도 주식 사자!",
            "detailed_description01": '''
               두려움은 수익을 늦출 뿐🦁
               ''',

            "detailed_description02": '''
               투자에서 높은 리스크를 감수하며, 
               큰 수익을 기대합니다. 
               변동성이 큰 시장에서도 
               과감한 결정을 내리는 편입니다. 
               주식, 암호화폐, 신기술 관련 자산에 
               적극적으로 투자합니다.   
               단기적 수익 실현에 초점을 맞추며, 
               주식시장의 급격한 변동에도 
               불안감을 느끼지 않고 
               적극적으로 대응합니다.  
               ''',

            "detailed_description03": '''
                주식 및 암호화폐와 같은 고위험 자산에 투자하되, 
                적정한 비율로 포트폴리오를 분산하세요.   
                기술적 분석과 매수/매도 시점을 
                정확히 판단하는 것이 중요합니다.   
                변동성이 높은 시장에서는 
                손절매 기준을 명확히 설정하세요. 
               ''',

            "image_path": "survey/images/lion.png",
        },
        "독수리": {
            "mbti_type": "독수리",
            "mbti_description": "기회를 포착하는 수리!",
            "detailed_description01": '''
               타이밍은 내가 정해🦅
               ''',

            "detailed_description02": '''
                안정성과 성장 사이에서 균형을 맞추며, 
                상황에 따라 기회를 포착하여 투자합니다. 
                리스크를 회피하지 않으면서
                무리하지 않는 선에서 다양한 자산에 투자합니다.
                시장을 면밀히 분석하고 
                신중하게 투자하며, 
                고위험 고수익 상품에도 
                적당히 도전합니다.
               ''',

            "detailed_description03": '''        
                    시장의 기회를 탐색할 때 
                    지나치게 신중해지지 않도록 
                    적절한 결단력을 가지세요.
                    리스크가 큰 자산과 안전 자산을 
                    적절히 배분하여 안정성을 유지하세요.
                    새로운 투자 기회에 열린 태도를 가지되, 
                    충분한 정보를 수집하고 
                    분석한 후 결정하세요.
               ''',

            "image_path": "survey/images/eagle.png",
        },
        "거북이": {
            "mbti_type": "거북이",
            "mbti_description": "느리지만 꾸준한 북이!",
            "detailed_description01": '''
                끝까지 가면 내가 다 이겨!🐢
               ''',
            "detailed_description02": '''
                    투자에서 안정성과 장기적 성장을 중시합니다. 
                    위험을 최소화하면서 꾸준히 자산을 
                    늘려가는 방식을 선호합니다.
                    변동성이 낮은 자산에 투자하며, 
                    확실한 기회를 기다리는 전략을 활용합니다!
                   ''',

            "detailed_description03": '''
                    장기적인 안정적 수익을 위해 국채, 고정 수익 상품, 
                    우량주 및 ETF를 활용한 포트폴리오를 구축하세요.
                    단기적인 시장 변동에 민감하지 않고, 
                    꾸준히 목표를 유지하세요.
                    정기적으로 투자 성과를 검토하며, 
                    필요에 따라 조정하는 것이 중요합니다.
                   ''',
            "image_path": "survey/images/turtle.png",
        },
        "고슴도치": {
            "mbti_type": "고슴도치",
            "mbti_description": "안전 제일 도치!",
            "detailed_description01": '''
               잃지 않는게 가장 중요하다구🦔
               ''',
            "detailed_description02": '''
                    자산 보호를 최우선으로 생각하며, 
                    안정적이고 변동성이 
                    적은 투자 상품을 선호합니다. 
                    리스크를 극도로 꺼리며,
                    수익보다는 자본 보존이 목표입니다.
                    국채, 고정 수익 상품, 예금 등에 주로 투자하며,
                    시장 변동성에 매우 민감하게 반응합니다. 
                    ''',

            "detailed_description03": '''
                    국채나 고정 수익 상품 위주로 
                    포트폴리오를 구성하되, 
                    물가 상승률에 대비해 
                    일부 성장형 자산도 소량 포함하세요.
                    급격한 시장 변동에서 패닉 매도를 피하세요.
                    전문가의 조언이나 펀드 매니저를 활용한
                    보수적 투자 방법을 고려하세요.
                   ''',
            "image_path": "survey/images/hedgehog.png",
        },
    }

@login_required
def mbti_test(request):
    if request.method == "GET":
        # 테스트 페이지 표시
        return render(request, 'survey/mbti_test.html')
    elif request.method == "POST":
        # 제출된 점수 가져오기
        total_score = int(request.POST.get('total_score', 0))

        # 점수에 따른 결과 계산
        if total_score >= 45:
            result_type = "사자"
        elif total_score >= 30:
            result_type = "독수리"
        elif total_score >= 15:
            result_type = "거북이"
        else:
            result_type = "고슴도치"

        # 결과 저장
        InvestmentResult.objects.create(
            user_id=request.user.id,
            total_score=total_score,
            result_type=result_type
        )

        # 세션에 결과 저장
        request.session['mbti_result'] = {
            'type': result_type,
            'description': f"{result_type} 유형 설명"
        }

        # 결과 페이지로 리다이렉트
        return redirect('mbti_result')

@login_required
def mbti_result(request):
    # 세션에서 결과 가져오기
    mbti_result = request.session.get('mbti_result')

    if not mbti_result:
        return HttpResponse("테스트 결과가 없습니다. 다시 시도해주세요.")

    # 공통 데이터에서 결과 가져오기
    results = get_mbti_data()
    result_data = results.get(mbti_result['type'], {
        "mbti_type": "알 수 없음",
        "mbti_description" : "설명이 준비되지 않았습니다.",
        "detailed_description01": "설명이 준비되지 않았습니다.",
        "detailed_description02": "설명이 준비되지 않았습니다.",
        "detailed_description03": "설명이 준비되지 않았습니다.",
        "image_path": "",
    })


    # 데이터 처리
    mbti_description = result_data.get('mbti_description', '설명이 준비되지 않았습니다.')
    detailed_description01 = result_data.get('detailed_description01', '설명이 준비되지 않았습니다.')
    detailed_description02 = result_data.get('detailed_description02', '설명이 준비되지 않았습니다.')
    detailed_description03 = result_data.get('detailed_description03', '설명이 준비되지 않았습니다.')

    return render(request, 'survey/mbti_result.html', {
        'result_type': result_data['mbti_type'],
        'mbti_description' : mbti_description,
        'detailed_description01': detailed_description01,
        'detailed_description02': detailed_description02,
        'detailed_description03': detailed_description03,
        'image_path': result_data.get('image_path', ''),
    })

