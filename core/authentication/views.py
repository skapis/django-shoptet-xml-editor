from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib import auth


class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = auth.authenticate(username=username, password=password)

            if user:
                if user.is_active:
                    auth.login(request, user)
                    return redirect('home')
                messages.error(request, 'Účet není aktivní, prosím kontaktujte HR oddělení')
                return render(request, 'authentication/login.html')

            messages.error(request, 'Špatné uživatelské jméno nebo heslo')
            return render(request, 'authentication/login.html')

        messages.error(request, 'Prosím vyplňte všechna povinná pole')
        return render(request, 'authentication/login.html')


class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        return redirect('login')
