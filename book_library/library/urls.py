from django.urls import path
from . import views

urlpatterns = [
    path('books/', views.book_list, name='book_list'),
    path('books/<int:book_id>/', views.book_detail, name='book_detail'),
    path('books/<int:book_id>/mark_as_read/', views.mark_as_read, name='mark_as_read'),
    path('books/<int:book_id>/remove_from_history/', views.remove_from_history, name='remove_from_history'),
    path('books/<int:book_id>/add_to_favorites/', views.add_to_favorites, name='add_to_favorites'),
    path('books/<int:book_id>/remove_from_favorites/', views.remove_from_favorites, name='remove_from_favorites'),
    path('books/<int:book_id>/download_description/', views.download_book_description, name='download_book_description'),
    path('reviews/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    path('favorites/', views.favorites_list, name='favorites_list'),
    path('history/', views.history, name='history'),
]
