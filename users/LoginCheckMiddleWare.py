from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseRedirect
from django.urls import reverse



class LoginCheckMiddleWare(MiddlewareMixin):

    def process_view(self,request,view_func,view_args,view_kwargs):
        modulename=view_func.__module__
        user=request.user
        
        if user.is_authenticated:
            if user.user_type == "1":
                if modulename == "users.adminViews":
                    pass
                elif modulename == "users.views" or modulename == "django.views.static" or modulename == "django.contrib.auth.views" or modulename == "upload.views" or modulename == "search.views":
                    pass
                else:
                    return HttpResponseRedirect(reverse("users:admin_home"))
            
            elif user.user_type == "2":
                if modulename == "users.userViews":
                    pass
                elif modulename == "users.views" or modulename == "django.views.static" or modulename == "django.contrib.auth.views" or modulename == "upload.views" or modulename == "search.views":
                    pass
                else:
                    return HttpResponseRedirect(reverse("users:user_home"))
            else:
                return HttpResponseRedirect(reverse("users:login"))

        else:
            if request.path == reverse("users:login") or request.path == reverse("users:doLogin") or modulename == "django.contrib.auth.views":
                pass
            else:
                return HttpResponseRedirect(reverse("users:login"))