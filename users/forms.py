from django import forms

# Start From Here.

class TextInput(forms.TextInput):
    input_type = "text"


class FileInput(forms.FileInput):
    input_type = "file"


class CreateUserForm(forms.Form):
	email=forms.EmailField(label="Email",max_length=50,widget=forms.EmailInput(attrs={"class":"form-control"}))
	password=forms.CharField(label="Password",max_length=50,widget=forms.PasswordInput(attrs={"class":"form-control"}))
	first_name=forms.CharField(label="First Name",widget=TextInput(attrs={"class":"form-control"}))
	last_name=forms.CharField(label="Last Name",max_length=50,widget=TextInput(attrs={"class":"form-control"}))
	username=forms.CharField(label="Username",max_length=50,widget=TextInput(attrs={"class":"form-control"}))
	address=forms.CharField(label="Address",max_length=50,widget=TextInput(attrs={"class":"form-control"}))
	profile_pic=forms.FileField(label="Profile Pic",max_length=50,widget=FileInput(attrs={"class":"form-control"}))


class EditUserForm(forms.Form):
	email=forms.EmailField(label="Email",max_length=50,widget=forms.EmailInput(attrs={"class":"form-control"}))
	first_name=forms.CharField(label="First Name",widget=TextInput(attrs={"class":"form-control"}))
	last_name=forms.CharField(label="Last Name",max_length=50,widget=TextInput(attrs={"class":"form-control"}))
	username=forms.CharField(label="Username",max_length=50,widget=TextInput(attrs={"class":"form-control"}))
	address=forms.CharField(label="Address",max_length=50,widget=TextInput(attrs={"class":"form-control"}))
	profile_pic=forms.FileField(label="Profile Pic",max_length=50,widget=FileInput(attrs={"class":"form-control"}),required=False)