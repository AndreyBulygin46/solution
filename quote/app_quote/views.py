from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegisterForm, LoginForm
from .models import Quote, ViewCounter, Vote
from django.contrib.auth.decorators import login_required
import random

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.user
            login(request, user)
            return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})


def home(request):
    quotes = list(Quote.objects.all())

    if not quotes:
        return render(request, 'home.html', {
            'quote': None,
            'view_count': 0,
            'no_quotes_message': "Еще нет цитат."
            })

    weights = [q.weight for q in quotes]
    selected_quote = random.choices(quotes, weights=weights, k=1)[0]

    view_counter, created = ViewCounter.objects.get_or_create(quote=selected_quote)
    view_counter.count += 1
    view_counter.save()

    context = {
        'quote': selected_quote,
        'view_count': view_counter.count,
    }

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')

        vote_type = request.POST.get('vote')
        if vote_type in ['like', 'dislike']:
            is_like = vote_type == 'like'
            vote, created = Vote.objects.get_or_create(user=request.user, quote=selected_quote)
            vote.is_like = is_like
            vote.save()

    return render(request, 'home.html', context)


@login_required
def delete_quote(request, quote_id):
    quote = get_object_or_404(Quote, id=quote_id)
    if request.user == quote.author:
        quote.delete()
    else:
        return HttpResponseForbidden("Вы можете удалять только свои цитаты.")
    return redirect('home')


