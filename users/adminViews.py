from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse  
from django.contrib.auth import authenticate, login, logout
from django.core.files.storage import FileSystemStorage
from users.EmailBackEnd import EmailBackEnd 
from django.contrib import messages
from users.models import CustomUser, Users
from users.forms import CreateUserForm, EditUserForm

# Create your views here.

def admin_home_view(request):
    return render(request,"users/admin/home_content.html")


def create_user_view(request):
    form=CreateUserForm()
    return render(request,"users/admin/admin_user_control/create_user.html", {"form":form})


def create_user_save(request):
    if request.method!="POST":
        return HttpResponse("Method Not Allowed")
    else:
        form=CreateUserForm(request.POST,request.FILES)
        if form.is_valid():
            first_name=form.cleaned_data["first_name"]
            last_name=form.cleaned_data["last_name"]
            username=form.cleaned_data["username"]
            email=form.cleaned_data["email"]
            password=form.cleaned_data["password"]
            address=form.cleaned_data["address"]

            profile_pic=request.FILES['profile_pic']
            fs=FileSystemStorage()
            filename=fs.save(profile_pic.name,profile_pic)
            profile_pic_url=fs.url(filename)
            
            try:
                user=CustomUser.objects.create_user(username=username,password=password,email=email,last_name=last_name,first_name=first_name,user_type=2)
                user.users.address=address
                user.users.profile_pic=profile_pic_url
                user.save()
                messages.success(request,"Successfully Added User")
                return HttpResponseRedirect(reverse("users:create_user"))
            except:
                messages.error(request,"Failed to Add User")
                return HttpResponseRedirect(reverse("users:create_user"))
        else:
            form=CreateUserForm(request.POST)
            return render(request,"users/admin/admin_user_control/create_user.html", {"form":form})
    


def edit_user(request,user_id):
    request.session['user_id']=user_id
    user=Users.objects.get(admin=user_id)
    form=EditUserForm()
    form.fields['email'].initial=user.admin.email
    form.fields['first_name'].initial=user.admin.first_name
    form.fields['last_name'].initial=user.admin.last_name
    form.fields['username'].initial=user.admin.username
    form.fields['address'].initial=user.address
    return render(request,"users/admin/admin_user_control/edit_user.html",{"form":form,"id":user_id,"username":user.admin.username})


def edit_user_save(request):
    if request.method!="POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        user_id=request.session.get("user_id")
        if user_id==None:
            return HttpResponseRedirect(reverse("users:all_users"))
        
        form=EditUserForm(request.POST,request.FILES)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            address = form.cleaned_data["address"]

            if request.FILES.get('profile_pic',False):
                profile_pic=request.FILES['profile_pic']
                fs=FileSystemStorage()
                filename=fs.save(profile_pic.name,profile_pic)
                profile_pic_url=fs.url(filename)
            else:
                profile_pic_url=None

            try:
                user=CustomUser.objects.get(id=user_id)
                user.first_name=first_name
                user.last_name=last_name
                user.email=email
                user.username=username
                user.save()

                user_model=Users.objects.get(admin=user_id)
                user_model.address=address
                if profile_pic_url!=None:
                    user_model.profile_pic=profile_pic_url
                user_model.save()
                del request.session['user_id']
                messages.success(request,"Successfully Changed User Details")
                return HttpResponseRedirect(reverse("users:edit_user",kwargs={"user_id":user_id}))
            except:
                messages.error(request,"Failed to Change User Details")
                return HttpResponseRedirect(reverse("users:edit_user",kwargs={"user_id":user_id}))
        else:
            form=EditStudentForm(request.POST)
            user=Users.objects.get(admin=user_id)
            return render(request,"users/admin/admin_user_control/edit_user.html",{"form":form,"id":user_id,"username":user.admin.username})
            


def manage_all_users(request):
    users=Users.objects.all()
    return render(request,"users/admin/admin_user_control/all_users.html",{"users":users})


