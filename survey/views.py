from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .models import Question, InvestmentResult
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse

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
    return redirect('index')



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
        "detailed_description": "",
        "mbti_description": "결과가 없습니다",
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
        'detailed_description': user_result['detailed_description'],
        'image_path': user_result.get('image_path', 'survey/images/person.jpg'),
        'stock_list': stock_list,
    }

    return render(request, 'survey/mypage.html', context)

# mbti 기능
def get_mbti_data():
    return {
        "사자": {
            "mbti_type": "사자",
            "mbti_description": "자신감과 용기로 도전을 마다하지 않는 대담한 투자자입니다.",
            "detailed_description": '''
                사자는 사냥을 위해 위험을 감수하며, 자신보다 강한 상대와도 맞서 싸우는 대담함을 보여줍니다.
                리더십과 용기를 갖춘 사자는 무리의 중심에서 가장 큰 책임을 지며, 실패의 가능성을 두려워하지 않습니다.
                상황이 어려울수록 더 대담하게 나아가며, 목표를 끝까지 추구합니다.
                
                - 유형 설명   
                - 특징: 투자에서 높은 리스크를 감수하며, 큰 수익을 기대합니다. 변동성이 큰 시장에서도 과감한 결정을 내리는 편입니다. 주식, 암호화폐, 신기술 관련 자산에 적극적으로 투자합니다.   
                - 투자 경향: 단기적 수익 실현에 초점을 맞추며, 주식시장의 급격한 변동에도 불안감을 느끼지 않고 적극적으로 대응합니다.   
               
               - 해당 유형에 맞는 투자 팁   
                - 팁: 주식 및 암호화폐와 같은 고위험 자산에 투자하되, 적정한 비율로 포트폴리오를 분산하세요.   
                - 기술적 분석과 매수/매도 시점을 정확히 판단하는 것이 중요합니다.   
                - 변동성이 높은 시장에서는 손절매 기준을 명확히 설정하세요.   
               ''',
            "image_path": "survey/images/lion.png",
        },
        "독수리": {
            "mbti_type": "독수리",
            "mbti_description": "신중히 기회를 선별하며 행동하는 전략가입니다.",
            "detailed_description": '''
               독수리는 에너지를 낭비하지 않고, 필요한 순간에만 강렬하게 행동합니다.
               ''',
            "image_path": "survey/images/eagle.png",
        },
        "비버": {
            "mbti_type": "비버",
            "mbti_description": "안정적인 기반을 추구하며 효율적으로 환경을 활용하는 유형입니다.",
            "detailed_description": '''
               비버는 안정적인 기반과 균형 잡힌 성장을 중요시합니다.
               ''',
            "image_path": "survey/images/beaver.png",
        },
        "고슴도치": {
            "mbti_type": "고슴도치",
            "mbti_description": "위험을 피하고 방어에 능한 신중한 유형입니다.",
            "detailed_description": '''
               고슴도치는 위험이 없는 환경을 선호하며 항상 자신을 보호합니다.
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
        "detailed_description": "설명이 준비되지 않았습니다.",
    })

    # 동적으로 단락 나누기
    detailed_descriptions = result_data['detailed_description'].split("\n\n")  # 빈 줄 기준으로 단락 구분

    return render(request, 'survey/mbti_result.html', {
        'result_type': result_data['mbti_type'],  # 결과 유형
        'result_descriptions': detailed_descriptions,  # 단락 리스트
        'image_path': result_data.get('image_path', ''),  # 이미지 경로
    })

# 관심 주식
@login_required
def mystock(request):
    return render(request, 'survey/mystock.html')



# 핫토픽
@login_required
def hot_topic(request):
    return render(request, 'survey/hot_topic.html')



# 주식 추천
@login_required
def stock_recommendations(request):
    return render(request, 'survey/stock_recommendations.html')
