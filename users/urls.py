from django.urls import path
from . import views
from . import adminViews
from . import userViews

app_name = 'users'

urlpatterns = [
        
        #...login-logout related urls...#

        path('login/', views.login_view, name='login'),
        path('doLogin', views.doLogin, name='doLogin'),
        path('get_user_details', views.GetUserDetails, name='user_details'),
        path('logout', views.logout_user, name='logout'),
        
        #...admin related urls...#

        path('admin_home', adminViews.admin_home_view, name='admin_home'),
        path('create_user', adminViews.create_user_view, name='create_user'), 
        path('create_user_save', adminViews.create_user_save, name='create_user_save'), 
        path('edit_user/<str:user_id>', adminViews.edit_user,name="edit_user"),
        path('edit_user_save', adminViews.edit_user_save,name="edit_user_save"),
        path('all_users', adminViews.manage_all_users, name='all_users'), 
        
        #...user realted urls...#
        
        path('user_home', userViews.user_home_view, name="user_home"),
        
    
        ]



      