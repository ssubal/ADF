from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse  
from django.contrib.auth import authenticate, login, logout
from users.EmailBackEnd import EmailBackEnd 
from django.contrib import messages
from users.models import Users

# Create your views here.


def login_view(request):
    return render(request,"users/accounts/login.html")


def doLogin(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        user=EmailBackEnd.authenticate(request,username=request.POST.get("email"),password=request.POST.get("password"))
        if user!=None:
            login(request,user)
            if user.user_type=="1":
                return HttpResponseRedirect(reverse("users:admin_home"))
            else:
                return HttpResponseRedirect(reverse("users:user_home"))
        else:
            messages.error(request,"Invalid Login Details")
            return HttpResponseRedirect(reverse("users:login"))


def GetUserDetails(request):
    if request.user!=None:
        return HttpResponse("User : "+request.user.email+" usertype : "+request.user.user_type)
    else:
        return HttpResponse("Please Login First")


def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse("users:login")) 


def user_home_view(request):
    return render(request,"users/user/home_content.html")





