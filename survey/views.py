from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .models import Question, InvestmentResult
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from datetime import datetime

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
            return redirect('index')  # 홈 페이지로 리디렉션
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
    return render(request, 'survey/News_home.html')
@login_required
def hot_topic(request):
    return render(request, 'survey/hot_topic.html')
@login_required
def daily_analysis(request):
    return render(request, 'survey/daily_analysis.html')
@login_required
def daily_analysis(request):
    analysis_date = datetime.now().strftime("%Y.%m.%d(%a)")
    context = {
        'analysis_date': analysis_date,
    }
    return render(request, 'survey/daily_analysis.html', context)


# 금융성향테스트
def get_mbti_data():
    return {
        "사자": {
            "mbti_type": "사자",
            "mbti_description": "자신감과 용기 사자!",
            "detailed_description01": '''
                사자는 사냥을 위해 위험을 감수하며, 자신보다 강한 상대와도 맞서 싸우는 대담함을 보여줍니다.
                리더십과 용기를 갖춘 사자는 무리의 중심에서 가장 큰 책임을 지며, 실패의 가능성을 두려워하지 않습니다.
                상황이 어려울수록 더 대담하게 나아가며, 목표를 끝까지 추구합니다.
               ''',

            "detailed_description02": '''
               투자에서 높은 리스크를 감수하며, 큰 수익을 기대합니다. 변동성이 큰 시장에서도 과감한 결정을 내리는 편입니다. 주식, 암호화폐, 신기술 관련 자산에 적극적으로 투자합니다.   
               단기적 수익 실현에 초점을 맞추며, 주식시장의 급격한 변동에도 불안감을 느끼지 않고 적극적으로 대응합니다.  
               ''',

            "detailed_description03": '''
                주식 및 암호화폐와 같은 고위험 자산에 투자하되, 적정한 비율로 포트폴리오를 분산하세요.   
                - 기술적 분석과 매수/매도 시점을 정확히 판단하는 것이 중요합니다.   
                - 변동성이 높은 시장에서는 손절매 기준을 명확히 설정하세요. 
               ''',

            "image_path": "survey/images/lion.png",
        },
        "독수리": {
            "mbti_type": "독수리",
            "mbti_description": "목표에만 들어가는 수리!",
            "detailed_description01": '''
               타이밍은 내가 정해🦅
               ''',

            "detailed_description02": '''

                안정성과 성장 사이에서 균형을 맞추며, 상황에 따라 기회를 포착하여 투자합니다. 리스크를 회피하지 않으면서도 무리하지 않는 선에서 다양한 자산에 투자합니다.
                시장을 면밀히 분석하고 신중하게 투자하며, 고위험 고수익 상품에도 적당히 도전합니다.
               ''',

            "detailed_description03": '''

                    시장의 기회를 탐색할 때 지나치게 신중해지지 않도록 적절한 결단력을 가지세요.
                    리스크가 큰 자산과 안전 자산을 적절히 배분하여 안정성을 유지하세요.
                    새로운 투자 기회에 열린 태도를 가지되, 충분한 정보를 수집하고 분석한 후 결정하세요.
               ''',

            "image_path": "survey/images/eagle.png",
        },
        "비버": {
            "mbti_type": "비버",
            "mbti_description": "안정적인 기반을 추구하며 효율적으로 환경을 활용하는 건축가!",
            "detailed_description01": '''
               비버는 안정적인 기반과 균형 잡힌 성장을 중요시합니다.
               ''',
            "detailed_description02": '''
                    투자에 있어서 안정성과 수익성을 모두 고려합니다. 장기적인 자산 성장을 목표로 하며, 분산 투자 전략을 선호합니다.
                    위험을 최소화하면서도 꾸준한 성장을 도모하며, 대형 우량주와 ETF에 주로 투자합니다.
                   ''',

            "detailed_description03": '''
                    장기적으로 안정적인 수익을 위해 대형 우량주, ETF, 채권 등을 활용한 분산 투자를 강화하세요.
                    시장 변화에 대응하여 정기적으로 포트폴리오를 검토하세요.
                    단기적 손실에 민감하지 말고 장기적 목표를 유지하세요.
                   ''',
            "image_path": "survey/images/beaver.png",
        },
        "고슴도치": {
            "mbti_type": "고슴도치",
            "mbti_description": "위험을 피하고 방어에 능한 '안전제일'주의자!",
            "detailed_description01": '''
               고슴도치는 위험이 없는 환경을 선호하며 항상 자신을 보호합니다.
               ''',
            "detailed_description02": '''
                    자산 보호를 최우선으로 생각하며, 안정적이고 변동성이 적은 투자 상품을 선호합니다. 리스크를 극도로 꺼리며, 수익보다는 자본 보존이 목표입니다.
                    투자 경향: 국채, 고정 수익 상품, 예금 등에 주로 투자하며, 시장 변동성에 매우 민감하게 반응합니다. 
                    ''',

            "detailed_description03": '''
                    국채나 고정 수익 상품 위주로 포트폴리오를 구성하되, 물가 상승률에 대비해 일부 성장형 자산도 소량 포함하세요.
                    급격한 시장 변동에서 패닉 매도를 피하세요.
                    전문가의 조언이나 펀드 매니저를 활용한 보수적 투자 방법을 고려하세요.
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
            result_type = "비버"
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


