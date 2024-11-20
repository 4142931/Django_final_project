console.log("JavaScript loaded");
// JavaScript for navigating between questions
function nextQuestion(currentQuestion) {
    // Hide current question
    document.getElementById(`question-${currentQuestion}`).style.display = 'none';

    // Show next question
    const nextQuestion = currentQuestion + 1;
    const nextQuestionElement = document.getElementById(`question-${nextQuestion}`);
    if (nextQuestionElement) {
        nextQuestionElement.style.display = 'block';

        // Update progress bar
        const progressBar = document.getElementById('progress-bar');
        const progressValue = nextQuestion * 10; // 예시로 10%씩 증가하도록 설정
        progressBar.style.width = `${progressValue}%`;
        progressBar.setAttribute('aria-valuenow', progressValue);
    } else {
        alert('모든 질문이 완료되었습니다. 감사합니다!');
    }
}