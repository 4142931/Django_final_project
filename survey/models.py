

from django.db import models


class Question(models.Model):
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=255)
    score = models.IntegerField()

    def __str__(self):
        return f"{self.text} ({self.score})"


class InvestmentResult(models.Model):
    user_id = models.CharField(max_length=255)  # 예시로 user_id 필드를 추가, 사용자가 로그인한 경우를 가정
    total_score = models.IntegerField()
    result_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)