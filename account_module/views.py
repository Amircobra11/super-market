from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login, logout
from django.urls import reverse
from django.template.loader import render_to_string
from django.views import View
from account_module.forms import RegisterForm, LoginForm, ForgotPasswordForm, ResetPasswordForm
from .models import User
from django.utils.crypto import get_random_string
from django.http import Http404
from utils.email_service import send_mail


class RegisterView(View):
    def get(self, request):
        register_form = RegisterForm()
        context = {
            'register_form': register_form
        }
        return render(request, 'account_module/register.html', context)

    def post(self, request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user_email = register_form.cleaned_data['email']
            user_password = register_form.cleaned_data['password']
            user: User = User.objects.filter(email__iexact=user_email).exists()
            if user:
                register_form.add_error('email', 'ایمیل وارد شده تکراری می باشد')
            else:
                new_user = User(email=user_email,
                                email_active_code=get_random_string(72),
                                is_active=False,
                                username=user_email, )
                new_user.set_password(user_password)
                new_user.save()

                send_mail('فعال سازی حساب کاربری', '', "amir.sisi.cobra11.com@gmail.com", {new_user.email},
                          html_message=render_to_string('emails/actvate_account.html', {'user': new_user}))
                return redirect(reverse('login_page'))
        context = {
            'register_form': register_form
        }
        return render(request, 'account_module/register.html', context)


class ActivateAccountView(View):
    def get(self, request, email_active_code):
        user: User = User.objects.get(email__exact=email_active_code).first()
        if user is not None:
            if not user.is_active:
                user.is_active = True
                user.email_active_code = get_random_string(72)
                user.save()
                # todo: show success message to user
                return redirect(reverse('login_page'))
            else:
                # todo: show your account was activated message to user
                pass

        raise Http404


class LoginView(View):

    def get(self, request):
        login_form = LoginForm()
        context = {
            'login_form': login_form
        }
        return render(request, 'account_module/login.html', context)

    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            email = login_form.cleaned_data['email']
            password = login_form.cleaned_data['password']
            user: User = User.objects.filter(email__iexact=email).first()
            if user is not None:
                if not user.is_active:
                    login_form.add_error('email', 'حساب کاربری شما فعال نشده است.')
                else:
                    is_password_correct = user.check_password(password)
                    if is_password_correct:
                        login(request, user)
                        return redirect(reverse('home_page'))
                    else:
                        login_form.add_error('email', 'کلمه عبور یا ایمیل اشتباه است.')
            else:
                login_form.add_error('email', 'کلمه عبور یا ایمیل اشتباه است.')

        context = {
            'login_form': login_form
        }
        return render(request, 'account_module/login.html', context)


class ForgotPasswordView(View):
    def get(self, request):
        forgot_password_form = ForgotPasswordForm()
        context = {
            'forgot_password_form': forgot_password_form
        }
        return render(request, 'account_module/forgot_password.html', context)

    def post(self, request):
        forgot_password_form = ForgotPasswordForm(request.POST)
        if forgot_password_form.is_valid():
            user_email = forgot_password_form.cleaned_data.get('email')
            user: User = User.objects.filter(email__exact=user_email).first()
            if user is not None:
                send_mail('فعال سازی حساب کاربری', '', "amir.sisi.cobra11.com@gmail.com", {user.email},
                          html_message=render_to_string('emails/forgot_password.html', {'user': user}))
                return redirect(reverse('login_page'))
        context = {
            'forgot_password_form': forgot_password_form
        }
        return render(request, 'account_module/forgot_password.html', context)


class ResetPasswordView(View):
    def get(self, request, active_code):
        user: User = User.objects.filter(email_active_code__exact=active_code).first()
        if user is None:
            return redirect(reverse('login_page'))

        reset_password_form = ResetPasswordForm()
        context = {
            'reset_password_form': reset_password_form,
            'user': user
        }
        return render(request, 'account_module/reset_forgot_password.html', context)

    def post(self, request, active_code):
        reset_password_form = ResetPasswordForm(request.POST)
        user: User = User.objects.filter(email__exact=active_code).first()
        if reset_password_form.is_valid():
            if user is None:
                return redirect(reverse('login_page'))
            else:
                user_new_password = reset_password_form.cleaned_data.get('password')
                user.set_password(user_new_password)
                user.email_active_code = get_random_string(72)
                user.is_active = True
                user.save()
                return redirect(reverse('login_page'))

        context = {
            'reset_password_form': reset_password_form,
            'user': user
        }
        return render(request, 'account_module/reset_forgot_password.html', context)


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect(reverse('login_page'))
