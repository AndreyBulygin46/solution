from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import RegisterForm, LoginForm, AddQuoteForm
from .models import Quote, ViewCounter, Vote
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
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
            'no_quotes_message': "Еще нет цитат.",
        })

    weights = [q.weight for q in quotes]
    selected_quote = random.choices(quotes, weights=weights, k=1)[0]

    view_counter, created = ViewCounter.objects.get_or_create(quote=selected_quote)
    view_counter.count += 1
    view_counter.save()

    context = {
        'quote': selected_quote,
        'view_count': view_counter.count,
        'author': selected_quote.author.username,
        'create_at': selected_quote.created_at,
        'user_vote': None,
        'has_voted': False,
    }

    context.update({
        'like_count': selected_quote.like_count(),
        'dislike_count': selected_quote.dislike_count(),
    })

    if request.user.is_authenticated:
        try:
            user_vote = Vote.objects.get(user=request.user, quote=selected_quote)
            context['user_vote'] = user_vote.is_like
            context['has_voted'] = True
        except Vote.DoesNotExist:
            pass

    # views.py
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')

        vote_type = request.POST.get('vote')
        if vote_type in ['like', 'dislike']:
            is_like = vote_type == 'like'
            try:
                vote = Vote.objects.get(user=request.user, quote=selected_quote)
                vote.is_like = is_like
                vote.save()
            except Vote.DoesNotExist:
                Vote.objects.create(
                    user=request.user,
                    quote=selected_quote,
                    is_like=is_like
                )
            messages.success(request, f"{'Лайк' if is_like else 'Дизлайк'} установлен.")
            return redirect('home')


    return render(request, 'home.html', context)


@login_required
def delete_quote(request, quote_id):
    quote = get_object_or_404(Quote, id=quote_id)
    if request.user == quote.author:
        quote.delete()
        messages.success(request, "Цитата успешно удалена.")
    return redirect('home')


@login_required
def add_quote(request):
    if request.method == 'POST':
        form = AddQuoteForm(request.POST)
        if form.is_valid():
            quote = form.save(commit=False)
            quote.author = request.user
            quote.save()
            return redirect('home')
    else:
        form = AddQuoteForm()
    return render(request, 'quotes/add_quote.html', {'form': form})

def popular_quotes(request):
    quotes = Quote.objects.annotate(
        like_count=Count('vote', filter=Q(vote__is_like=True))
    ).order_by('-like_count')

    context = {
        'quotes': quotes,
    }

    return render(request, 'popular.html', context)