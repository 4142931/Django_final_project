from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# TF-IDF 벡터화
def tfidf_vectorize(corpus):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(corpus)
    return tfidf_matrix, vectorizer

def train_svm(tfidf_matrix, labels):
    X_train, X_test, y_train, y_test = train_test_split(tfidf_matrix, labels, test_size=0.2, random_state=42)
    svm_model = SVC(kernel='linear', random_state=42)
    svm_model.fit(X_train, y_train)
    y_pred = svm_model.predict(X_test)
    print(f"SVM 정확도: {accuracy_score(y_test, y_pred) * 100:.2f}%")
    return svm_model

def predict_labels(svm_model, vectorizer, articles):
    tfidf_matrix = vectorizer.transform(articles)
    predictions = svm_model.predict(tfidf_matrix)
    return predictions


