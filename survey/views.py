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
def mypage_view(request):
    return render(request, 'survey/mypage.html')



# mbti 기능
@login_required
def mbti(request):
    return render(request, 'survey/mbti.html')
@login_required
def mbti_lion(request):
    return render(request, 'survey/mbti_lion.html')


# 관심 주식
@login_required
def mystock(request):
    return render(request, 'survey/mystock.html')



# 핫토픽
def hot_topic(request):
    return render(request, 'survey/hot_topic.html')



# 주식 추천
def stock_recommendations(request):
    return render(request, 'survey/stock_recommendations.html')
