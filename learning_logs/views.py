from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect, Http404
from django.db import IntegrityError

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import Topic, Entry
from .forms import TopicForm, EntryForm

def index(request):
    """Домашняя страница приложения Learning Log"""
    return render(request, 'learning_logs/index.html')

@login_required
def topics (request):
    """Выводит список тем"""
    topics = Topic.objects.filter(owner=request.user).order_by('date_added')
    context = {'topics' : topics}
    return render(request, 'learning_logs/topics.html', context)

@login_required
def topic(request, topic_id):
    """Выводит одну тему и все ее записи."""
    topic = Topic.objects.get(id=topic_id)

    check_topic_owner(request)
    
    entries = topic.entry_set.order_by('-date_added')
    context = {'topic': topic, 'entries': entries}
    return render(request, 'learning_logs/topic.html', context)

@login_required
def new_topic(request):
    """Определяет новую тему."""
    if request.method != 'POST':
        # Данные не отправлялись; создается пустая форма.
        form = TopicForm()
    else:
        # Отправлены данные POST; обработать данные.
        try:
            form = TopicForm(request.POST)
            if form.is_valid():
                new_topic = form.save(commit=False)
                new_topic.owner = request.user
                new_topic.save()
                return HttpResponseRedirect(reverse('learning_logs:topics'))
            
        except IntegrityError:
                messages.error(request, 'Ошибка при создании темы. Попробуйте снова.')
                
    context = {'form': form}
    return render(request, 'learning_logs/new_topic.html', context)

@login_required
def new_entry(request, topic_id):
    """Добавляет новую запись по конкретной теме."""
    topic = Topic.objects.get(id=topic_id)

    if request.method != 'POST':
        # Данные не отправлялись; создается пустая форма.
        form = EntryForm()
    else:
        # Отправлены данные POST; обработать данные.
        try:
            form = EntryForm(data=request.POST)
            if form.is_valid() and request.user == topic.owner:
                new_entry = form.save(commit=False)
                new_entry.topic = topic
                new_entry.save()
                return HttpResponseRedirect(reverse('learning_logs:topic', args=[topic_id]))
            
        except IntegrityError:
                messages.error(request, 'Ошибка при создании записи. Попробуйте снова.')

    context = {'topic': topic, 'form': form}
    return render(request, 'learning_logs/new_entry.html', context)

@login_required
def edit_entry(request, entry_id):
    """Редактирует существующую запись."""
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic

    check_topic_owner(request)

    if request.method != 'POST':
        # Исходный запрос; форма заполняется данными текущей записи.
        form = EntryForm(instance=entry)
    else:
        # Отправка данных POST; обработать данные.
        try:
            form = EntryForm(instance=entry, data=request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('learning_logs:topic', args=[topic.id]))
            
        except IntegrityError:
            messages.error(request, 'Ошибка при редактировании записи. Попробуйте снова.')

    context = {'entry': entry, 'topic': topic, 'form': form}
    return render(request, 'learning_logs/edit_entry.html', context)

def check_topic_owner(request):
    """Проверка того, что тема принадлежит текущему пользователю."""
    if topic.owner != request.user:
        raise Http404