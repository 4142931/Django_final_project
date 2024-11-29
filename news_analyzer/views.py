from django.shortcuts import render

# Create your views here.
def example_view(request):
    return render(request, 'news_analyzer/example.html')