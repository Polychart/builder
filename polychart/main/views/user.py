"""
Tornado Request handlers for the user settings page (/settings)
"""
import django.db
import logging

from django                         import forms
from django.contrib.auth            import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models     import User
from django.core.exceptions         import ValidationError
from django.shortcuts               import render

from polychart.main       import models as m
from polychart.main.utils import secureStorage

class UserInfoForm(forms.Form):
  def __init__(self, *args, **kwargs):
    self.user = kwargs.pop('user', None)
    super(UserInfoForm, self).__init__(*args, **kwargs)

  email   = forms.EmailField(max_length = 75)
  name    = forms.CharField(max_length  = 30)
  company = forms.CharField(max_length  = 128, required = False)
  website = forms.CharField(max_length  = 128, required = False)

  def clean_email(self):
    email = self.cleaned_data['email']
    # see if any other user uses this email.
    if User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
      raise ValidationError('Email %s is already being used.' % email)
    return email

class PasswordForm(forms.Form):
  old  = forms.CharField(widget = forms.PasswordInput, required = True)
  new  = forms.CharField(widget = forms.PasswordInput, required = True)
  veri = forms.CharField(widget = forms.PasswordInput, required = True)

  def __init__(self, *args, **kwargs):
    self.user = kwargs.pop('user', None)
    super(PasswordForm, self).__init__(*args, **kwargs)

  def clean(self):
    if self.cleaned_data.get('new', None) != self.cleaned_data.get('veri', None):
      raise ValidationError("New passwords did not match.")
    return self.cleaned_data

  def clean_old(self):
    old = self.cleaned_data.get('old', None)
    if authenticate(username=self.user.username, password=old) != self.user:
      raise ValidationError("Old password is incorrect.")
    return old


@login_required
def userSettings(request):
  def createUserInfoForm(user):
    userInfo = m.UserInfo.objects.get(user=request.user)

    return UserInfoForm(
      initial={
        'company': userInfo.company,
        'email': user.email,
        'name': user.first_name,
        'website': userInfo.website,
      },
      user=request.user
    )

  if request.method == 'GET':
    return render(request, 'settings.tmpl', dict(
      userinfo_form=createUserInfoForm(request.user),
      password_form=PasswordForm()
    ))

  if request.method == 'POST':
    action = request.REQUEST.get('action', None)

    if action == 'change-pswd':
      user          = request.user
      password_form = PasswordForm(request.REQUEST, user = user)
      result        = None
      errorMsg      = None

      if password_form.is_valid():
        new = password_form.cleaned_data['new']
        user.set_password(new)
        user.save()

        salt = m.UserInfo.objects.get(user=user).secure_storage_salt
        request.session['secureStorageKey'] = secureStorage.getEncryptionKey(new, salt)

        result = 'success'
      else:
        if password_form.errors.get('__all__', None):
          errorMsg = password_form.errors['__all__'][0]
        else:
          errorMsg = "There was an error while updating the password."

        result = 'error'

      return render(request, 'settings.tmpl', dict(
        userinfo_form = createUserInfoForm(request.user),
        password_form = password_form,
        action        = action,
        result        = result,
        errorMsg      = errorMsg
      ))

    if action == 'update-info':
      user          = request.user
      userinfo_form = UserInfoForm(request.REQUEST, user = user)
      result        = None
      errorMsg      = None

      if userinfo_form.is_valid():
        user.email      = userinfo_form.cleaned_data['email']
        user.first_name = userinfo_form.cleaned_data['name']
        try:
          user.save()
        except django.db.IntegrityError:
          # TODO - error must be handled here.
          logging.exception('error while changing the email of the user.')
        else:
          # update the company info.
          userinfo         = user.userinfo
          userinfo.company = userinfo_form.cleaned_data['company']
          userinfo.website = userinfo_form.cleaned_data['website']
          userinfo.save()

          result = 'success'
      else:
        if userinfo_form.errors.get('__all__', None):
          errorMsg = userinfo_form.errors['__all__'][0]
        else:
          errorMsg = "There was an error while updating the personal information."

        result = 'error'

      return render(request, 'settings.tmpl', dict(
        userinfo_form = userinfo_form,
        password_form = PasswordForm(),
        action        = action,
        result        = result,
        errorMsg      = errorMsg
      ))

    return render(request, 'settings.tmpl')
