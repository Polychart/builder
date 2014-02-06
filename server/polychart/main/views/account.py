"""
Django handlers and functions related to user accounts.
"""
import django.db
import logging

from django                       import forms
from django.conf                  import settings
from django.contrib.auth          import login, authenticate, logout
from django.contrib.auth.models   import User
from django.core.exceptions       import ValidationError
from django.shortcuts             import redirect, render
from django.views.decorators.http import require_http_methods

import polychart.main.models as m

from polychart.main.utils       import secureStorage
from polychart.main.utils.email import sendEmail, sendEmailAsync

try:
  from polychart.analytics.views import aliasUser
except ImportError:
  aliasUser = None

def accountLogin(request):
  """Django handler for user logins."""
  defaultRedirectUrl = '/home'

  if request.method == 'GET':
    if request.user.is_authenticated():
      return redirect(defaultRedirectUrl)

    return render(request, 'login.tmpl', dictionary=dict(
      redirectUrl=request.REQUEST.get('next', defaultRedirectUrl)
    ))

  if request.method == 'POST':
    username = request.POST['username']
    password = request.POST['password']
    success  = handleLogin(request, username, password)

    if success:
      redirectUrl = request.POST.get('next') or defaultRedirectUrl
      assert redirectUrl[0] == '/'
      return redirect(redirectUrl)

    return render(request, 'login.tmpl', dictionary=dict(
      redirectUrl = request.REQUEST.get('next', defaultRedirectUrl),
      username    = username,
      error       = 'auth'
    ))

def accountSignup(request):
  """Django handler for user signup."""

  # If the feature is disabled
  if not settings.SIGNUP_ENABLED:
    return redirect('/')

  def getRedirect():
    """Helper to get redirect."""
    redirectUrl = request.GET.get('redirect', '/home')

    if redirectUrl != 'payment':
      return redirect(redirectUrl)

    coupon = request.GET.get('c', None)
    if coupon:
      return redirect('/payment?c='+coupon)

    return redirect('/payment')

  if request.method == 'GET':
    if not request.user.is_authenticated():
      signupForm = SignupForm(initial=request.GET)
      return render(request, 'signup.tmpl', dictionary={
        'signup_form': signupForm
      })
    else:
      return getRedirect()

  if request.method == 'POST':
    # check to make sure plan is filled out ok
    signupForm = SignupForm(request.REQUEST)
    if not signupForm.is_valid():
      return render(request, 'signup.tmpl', dictionary={
        'signup_form': signupForm,
        'error':       'invalid'
      })

    # set up required fields
    success = handleSignup(request, signupForm.cleaned_data)

    if not success:
      # form is validated, but we have failed to create new user.
      return render(request, 'signup.tmpl', dictionary={
        'signup_form': signupForm,
        'error':       'unknown'
      })

    # new user successfullly created.
    return getRedirect()

def accountResetPassword(request):
  """Django handler to reset user passwords."""

  # Pylint does not detect Django model methods.
  # pylint: disable = E1101

  # If the feature is disabled
  if not settings.PASSWORD_RESET_ENABLED:
    return redirect('/')

  if request.method == 'GET':
    codeForm = ResetPasswordCodeForm(request.REQUEST)
    if codeForm.is_valid():
      token = codeForm.cleaned_data['token']
      return render(request, 'resetPassword.tmpl', dictionary=dict(
        username = token.user.username,
        code     = codeForm.cleaned_data['code'],
      ))
    else:
      # invalid token - redirect to the forgot-password page.
      return redirect('/forgot-password')

  if request.method == 'POST':
    codeForm = ResetPasswordCodeForm(request.REQUEST)
    passForm = ResetPasswordFinishForm(request.REQUEST)

    if (codeForm.is_valid() and passForm.is_valid()):
      # success code path.
      token = codeForm.cleaned_data['token']
      try:
        password = passForm.cleaned_data['password']
        user     = token.user
        user.set_password(password)
        user.save()
        newlyLoggedIn = authenticate(username=user.username, password=password)
        loginWithSecureStorage(request, newlyLoggedIn, password)
        return redirect('/home')
      finally:
        token.expire_and_save()
    else:
      # failure code path.
      if codeForm.is_valid():
        token = codeForm.cleaned_data['token']
        return render(request, 'resetPassword.tmpl', dictionary=dict(
          username = token.user.username,
          code     = codeForm.cleaned_data['code'],
        ))
      else:
        return redirect('/forgot-password')

def accountForgotPassword(request):
  """
  Django handler to deal with forgotten passwords.
  """

  # If the feature is disabled
  if not settings.PASSWORD_RESET_ENABLED:
    return redirect('/')

  if request.method == 'GET':
    return render(request, 'forgotPassword.tmpl')

  if request.method == 'POST':
    form   = ForgotPasswordForm(request.REQUEST)
    status = None

    if form.is_valid():
      user  =  form.cleaned_data['user']
      email = form.cleaned_data['username']

      token = m.ForgotPassword.objects.create(user=user)

      subject = 'Polychart.com password reset'
      body = """Hello,

You are receiving this message because someone (hopefully you!) has indicated that your password for polychart.com has been lost.

To reset your password, please follow the link below:

{link}

Thank you.

The Polychart Team"""
      params = {'link': token.link}
      sendEmail(subject, body, user.email, params=params)

      status = 'success'
    else:
      status = 'accountNotFound'

    return render(request, 'forgotPassword.tmpl', dictionary={
      'password_form': form,
      'status':        status,
    })

def accountLogout(request):
  """Django handler to deal with account logout."""
  if request.method == 'GET':
    request.session['secureSessionKey'] = None
    logout(request)
    return redirect('/')
  elif request.method == 'POST':
    request.session['secureSessionKey'] = None
    logout(request)
    return redirect('/')

class SignupForm(forms.Form):
  """Django class representing the user signup form."""
  username    = forms.CharField(max_length=75, widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))
  password    = forms.CharField(widget=forms.PasswordInput)
  email       = forms.EmailField(max_length=75)

  # Optional fields.
  first_name  = forms.CharField(max_length=30,  required=False)
  last_name   = forms.CharField(max_length=30,  required=False)
  company     = forms.CharField(max_length=128, required=False)
  title       = forms.CharField(max_length=128, required=False)
  phone       = forms.CharField(max_length=32,  required=False)
  technical   = forms.BooleanField(required=False)

  def clean_username(self):
    """Helper function to clean and validate usernames."""
    username = self.cleaned_data['username']
    if User.objects.filter(username=username).count() > 0:
      raise ValidationError('Username %s is already being used.' % username)
    return username

  def clean_first_name(self):
    """Helper function to clean and validate user-input first name."""
    name = self.cleaned_data['first_name']
    if not name:
      name = ''
    return name

  def clean_last_name(self):
    """Helper function to clean and validate user-input last name."""
    name = self.cleaned_data['last_name']
    if not name:
      name = ''
    return name

  def clean_email(self):
    """Helper function to clean and validate user-input email."""
    email = self.cleaned_data['email']
    if User.objects.filter(email=email).count() > 0:
      raise ValidationError('Email %s is already being used.' % email)
    return email

class ForgotPasswordForm(forms.Form):
  """Django form for forgotten passwords."""
  username = forms.CharField(max_length=75)
  def clean_username(self):
    """Helper function to clean and validate user-input username."""
    if 'username' in self.cleaned_data:
      username_or_email = self.cleaned_data['username']
    else:
      username_or_email = None
    user = m.username_or_email(username_or_email)
    if user is None:
      raise ValidationError('User or email %s does not exist.' % username_or_email)
    else:
      # set the user.
      self.cleaned_data['user'] = user
    return username_or_email

class ResetPasswordCodeForm(forms.Form):
  """Django form for resetting passwords."""
  code = forms.CharField(max_length=128, required=True)

  def clean_code(self):
    """Helper function to clean and validate password reset code."""
    code = self.cleaned_data['code']
    try:
      fp = m.ForgotPassword.objects.get(code=code,expired=False)
    except m.ForgotPassword.DoesNotExist:
      raise ValidationError('Invalid link.')
    else:
      self.cleaned_data['token'] = fp
    return code

class ResetPasswordFinishForm(forms.Form):
  """Django form for finishing password resets."""
  password = forms.CharField(required=True)

def createUser(data):
  """Helper function to create a new user in the database."""
  username   = data['username']
  password   = data['password']
  company    = data.get('company', '')
  title      = data.get('title', '')
  phone      = data.get('phone', '')
  email      = data.get('email', '')
  technical  = data.get('technical', '')
  usecase    = 'person'

  if 'name' in data:
    (first_name, x, last_name) = data['name'].partition(' ')
  else:
    first_name = data['first_name']
    last_name  = data['last_name']

  try:
    user = User.objects.create_user(username, email, password)
  except django.db.IntegrityError:
    logging.getLogger(__name__).exception('Error while creating the user.')
    return None

  user.first_name = first_name
  user.last_name  = last_name
  user.save()

  user_info = m.UserInfo.get_user_info(user)
  user_info.company   = company
  user_info.title     = title
  user_info.phone     = phone
  user_info.usecase   = usecase
  user_info.technical = technical
  user_info.save()
  user_authenticated = authenticate(username=username, password=password)
  assert user_authenticated, "Authentication failed for the new user."

  if settings.NEW_USER_EMAIL_ENABLED:
    subject = 'Hi {firstName}, Welcome to Polychart'
    body = """Hi {firstName},

My name is Samson Hu and I am a co-founder at Polychart. I would like to take the time to personally thank you for creating an account on our website.

As we are in beta, I am making myself available to you for any questions, concerns, or feedback that you may have.

If you would like help with deployment, feel free to reach out to me and we can setup a call where I can guide you through our on-boarding process.

Hope to hear from you soon,
Samson Hu
Co-founder at Polychart
Email: samson@polychart.com"""
    params = {'firstName': first_name}

    # Send new user email on separate thread
    sendEmailAsync(subject, body, user.email, params=params)

  return user_authenticated

def handleSignup(request, data):
  """Helper function to handle user signup."""
  user = createUser(data)
  if user is None:
    return False
  if aliasUser:
    aliasUser(request.session.session_key, user)

  loginWithSecureStorage(request, user, data['password'])
  return True

# Warning: does not check password
def loginWithSecureStorage(request, user, password):
  """Django handler to log user in with a secure storage key."""
  # Mark user as logged in via django auth
  login(request, user)

  # Compute user's secure storage key
  salt = m.UserInfo.objects.get(user=user).secure_storage_salt
  request.session['secureStorageKey'] = secureStorage.getEncryptionKey(password, salt)

def handleLogin(request, usernameOrEmail, password):
  '''
  Handle login.
  Returns true / false depending depending on the result of login.
  '''

  user = authenticate(username=usernameOrEmail, password=password)
  if user is None:
    # try for email.
    try:
      _user = User.objects.get(email=usernameOrEmail)
    except User.DoesNotExist:
      pass
    else:
      user = authenticate(username=_user.username, password=password)
  if user is not None:
    if user.is_active:
      loginWithSecureStorage(request, user, password)
      return True
    return False # disabled account
  return False # invalid login
