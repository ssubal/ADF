from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse  


# Create your views here.


def user_home_view(request):
    return render(request,"users/user/home_content.html")