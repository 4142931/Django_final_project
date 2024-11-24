// 점수를 저장할 전역 변수 정의
let totalScore = 0;

console.log("JavaScript loaded");

// JavaScript for navigating between questions
function nextQuestion(currentQuestion, score) {
    // 점수 누적
    totalScore += score;  // 사용자가 응답한 점수를 `totalScore`에 추가

    // 현재 질문 숨기기
    const currentQuestionElement = document.getElementById(`question-${currentQuestion}`);
    if (currentQuestionElement) {
        currentQuestionElement.style.display = 'none';
    }

    // 다음 질문 보이기
    const nextQuestion = currentQuestion + 1;
    const nextQuestionElement = document.getElementById(`question-${nextQuestion}`);
    if (nextQuestionElement) {
        nextQuestionElement.style.display = 'block';

        // 진행 바 업데이트
        const progressBar = document.getElementById('progress-bar');
        const progressValue = (nextQuestion / 20) * 100; // 20개 질문 기준으로 퍼센트 계산
        progressBar.style.width = `${progressValue}%`;
        progressBar.setAttribute('aria-valuenow', progressValue);
    } else {
        // 모든 질문 완료 후 서버로 결과 전송
        submitResults();
    }
}

// 결과 서버로 전송
function submitResults() {
    // 폼 생성
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/mbti_test/';  // Django view로 점수를 전송할 URL

    // CSRF 토큰 추가 (Django에서 보안 상 필요)
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = csrfToken;
    form.appendChild(csrfInput);

    // 점수 데이터를 폼에 추가
    const scoreInput = document.createElement('input');
    scoreInput.type = 'hidden';
    scoreInput.name = 'total_score';
    scoreInput.value = totalScore;  // 누적된 `totalScore` 값을 폼에 추가
    form.appendChild(scoreInput);

    // 폼 제출
    document.body.appendChild(form);
    form.submit();
}
