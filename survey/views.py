from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required

from .models import Question
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm


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
@login_required
def mypage_view(request): # 이미지 경로가 제대로 반응하지 않음
    # 사용자 MBTI 결과 준비
    user_mbti_type = "고슴도치"  # 이 부분은 테스트 결과에 따라 동적으로 결정됨

    # 결과 유형에 따라 다른 설명 및 이미지 경로를 설정
    results = {
        "사자": {
            "mbti_type": "사자",
            "mbti_description": "자신감과 용기로 위험을 정면으로 마주하며, 목표를 위해 어떤 도전도 피하지 않는 대담한 사냥꾼.",
            "detailed_description": '''
               사자는 사냥을 위해 위험을 감수하며, 자신보다 강한 상대와도 맞서 싸우는 대담함을 보여줍니다.
               리더십과 용기를 갖춘 사자는 무리의 중심에서 가장 큰 책임을 지며, 실패의 가능성을 두려워하지 않습니다.
               상황이 어려울수록 더 대담하게 나아가며, 목표를 끝까지 추구합니다.
               ''',
            "image_path": "survey/images/lion.png",
        },
        "독수리": {
            "mbti_type": "독수리",
            "mbti_description": "위험과 안전 사이에서 신중히 기회를 선별하는 하늘의 사냥꾼.",
            "detailed_description": '''
               높은 하늘에서 땅을 주시하며 먹잇감이 보일 때 정확히 낚아채는 독수리는 기회 선별형의 완벽한 상징입니다. 
               에너지를 낭비하지 않으며, 필요할 때만 강렬하게 행동합니다.
               ''',
            "image_path": "survey/images/eagle.png",
        },
        "비버": {
            "mbti_type": "비버",
            "mbti_description": "안정적인 기반을 통해 균형 있는 성장을 도모하며, 환경을 효율적으로 활용하는 현명한 건축가.",
            "detailed_description": '''
               비버는 강과 숲 사이의 환경을 균형 있게 활용하며, 
               튼튼한 댐을 지어 안전과 성장을 동시에 챙깁니다.
               위험 요소를 분석하며, 안전한 기반을 다져 나가는 성향이 강합니다.
               ''',
            "image_path": "survey/images/beaver.png",
        },
        "고슴도치": {
            "mbti_type": "고슴도치",
            "mbti_description": "자신을 보호하기 위한 방어 수단을 항상 준비하며, 위험한 상황을 피하는 신중한 생존자.",
            "detailed_description": '''
               고슴도치는 위험이 닥치면 자신의 가시를 세워 방어하며, 절대 무리하지 않습니다.
               안전한 환경에서만 움직이며, 위험이 없는 순간까지 침착함을 유지합니다.
               ''',
            "image_path": "survey/images/hedgehog.png",
        },
    }

    # 사용자의 결과에 맞는 설명 및 이미지 경로를 가져옵니다.
    user_result = results[user_mbti_type]

    # 실시간 관심 주식 목록 준비
    stock_list = [
        {
            'name': '삼성전자',
            'price': '71,500원',
            'change': '+1.25%',
            'change_class': 'positive',
            'image_path': 'survey/images/samsung.jpg',
            'description': '반도체 및 전자제품을 주요 사업으로 하는 대기업',
        },
        {
            'name': '카카오',
            'price': '123,000원',
            'change': '-0.85%',
            'change_class': 'negative',
            'image_path': 'survey/images/kakao.jpg',
            'description': '소셜 미디어 및 IT 플랫폼을 운영하는 한국의 IT 기업',
        },
    ]

    # Context에 두 데이터를 합쳐서 전달
    context = {
        'mbti_type': user_result['mbti_type'],
        'mbti_description': user_result['mbti_description'],
        'detailed_description': user_result['detailed_description'],
        'image_path': user_result['image_path'],
        'stock_list': stock_list,
    }

    return render(request, 'survey/mypage.html', context)

# mbti 기능
@login_required
def mbti_test(request):
    return render(request, 'survey/mbti_test.html')
@login_required
def mbti_result(request):
    return render(request, 'survey/mbti_result.html')


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
