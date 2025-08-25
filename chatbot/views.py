from django.contrib import auth
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from openai import OpenAI
from .models import Chat

# Use API key from settings (better than hardcoding)
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def ask_openai(message):
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # faster, cheaper, better
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message},
        ]
    )
    return response.choices[0].message.content.strip()

@login_required
def chatbot(request):
    chats = Chat.objects.filter(user=request.user)

    if request.method == 'POST':
        message = request.POST.get('message')
        response = ask_openai(message)

        chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        chat.save()

        return JsonResponse({'message': message, 'response': response})

    return render(request, 'chatbot.html', {'chats': chats})

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot')
        else:
            return render(request, 'login.html', {'error_message': 'Invalid username or password'})
    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                return redirect('chatbot')
            except:
                return render(request, 'register.html', {'error_message': 'Error creating account'})
        else:
            return render(request, 'register.html', {'error_message': "Passwords don't match"})
    return render(request, 'register.html')

def logout(request):
    auth.logout(request)
    return redirect('login')
