from django.shortcuts import render

def home(request):
    return render(request, "home.html")

def upload_page(request):
    return render(request, "upload.html")

def configure_page(request):
    return render(request, "configure.html")

def quiz_loading_page(request, quiz_id):
    return render(request, "quiz_loading.html", {"quiz_id": quiz_id})

def quiz_detail_page(request, quiz_id):
    return render(request, "quiz_detail.html", {"quiz_id": quiz_id})