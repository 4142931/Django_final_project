import sqlite3
from django.shortcuts import render


def stock_recommendations(request):
    conn = sqlite3.connect('stock/stock_recommendations.db')
    cursor = conn.cursor()

    # 데이터 조회
    cursor.execute("SELECT * FROM recommendations")
    recommendations = cursor.fetchall()
    conn.close()

    return render(request, 'stock_recommendations.html', {'recommendations': recommendations})

