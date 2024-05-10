from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import ReviewForm
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from textwrap import wrap  
from .models import Book, Review, Favorite, History

@login_required
def book_list(request):
    genre = request.GET.get('genre', None)
    genres = Book.objects.values_list('genre', flat=True).distinct()

    if genre:
        books = Book.objects.filter(genre=genre)
    else:
        books = Book.objects.all()

    return render(request, 'book/book_list.html', {'books': books, 'genres': genres, 'selected_genre': genre})

@login_required
def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    reviews = book.reviews.all()

    is_favorited = Favorite.objects.filter(user=request.user, book=book).exists()
    is_in_history = History.objects.filter(user=request.user, book=book).exists()

    form = ReviewForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        review = form.save(commit=False)
        review.book = book
        review.user = request.user
        review.save()
        messages.success(request, 'Ваш відгук успішно додано.')
        return redirect('book_detail', book_id=book_id)

    return render(
        request,
        'book/book_detail.html',
        {
            'book': book,
            'reviews': reviews,
            'form': form,
            'is_favorited': is_favorited,
            'is_in_history': is_in_history,
        }
    )


@login_required
def add_to_favorites(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if Favorite.objects.filter(user=request.user, book=book).exists():
        messages.warning(request, 'Ця книга вже в вашому списку обраного.')
    else:
        Favorite.objects.create(user=request.user, book=book)
        messages.success(request, 'Книгу додано до обраного.')

    return redirect('book_detail', book_id=book_id)

@login_required
def remove_from_favorites(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    favorite = Favorite.objects.filter(user=request.user, book=book)
    if favorite.exists():
        favorite.delete()
        messages.success(request, 'Книгу видалено з обраного.')
    else:
        messages.warning(request, 'Цієї книги немає у вашому списку обраного.')

    return redirect('book_detail', book_id=book_id)

@login_required
def history(request):
    history = History.objects.filter(user=request.user)
    return render(request, 'book/history.html', {'history': history})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Реєстрація успішна. Ласкаво просимо!')
            return redirect('book_list')
    else:
        form = UserCreationForm()

    return render(request, 'auth/register.html', {'form': form})

@login_required
def mark_as_read(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    History.objects.create(user=request.user, book=book)

    return redirect('book_detail', book_id=book_id)


@login_required
def remove_from_history(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    history_entry = History.objects.filter(user=request.user, book=book)
    if history_entry.exists():
        history_entry.delete()
        messages.success(request, 'Книгу видалено з історії прочитаних.')
    else:
        messages.warning(request, 'Цієї книги немає у вашій історії прочитаних.')

    return redirect('book_detail', book_id=book_id)

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if review.user != request.user:
        messages.error(request, 'Ви не маєте права видаляти цей відгук.')
        return redirect('book_list')

    book_id = review.book.id

    review.delete()

    messages.success(request, 'Відгук успішно видалено.')
    return redirect('book_detail', book_id=book_id)

@login_required
def favorites_list(request):
    favorites = Favorite.objects.filter(user=request.user)

    return render(request, 'book/favorites_list.html', {'favorites': favorites})

@login_required
def download_book_description(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{book.title}_description.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    p.setFont("Times-Roman", 12)

    text_object = p.beginText(50, 750)
    text_object.setFont("Times-Roman", 12)

    text_object.textLine(f"Title: {book.title}")
    text_object.textLine(f"Author: {book.author}")
    text_object.textLine(f"Genre: {book.genre}")

    description_lines = wrap(book.description, width=100)
    for line in description_lines:
        text_object.textLine(line)

    p.drawText(text_object)
    p.showPage()
    p.save()

    return response