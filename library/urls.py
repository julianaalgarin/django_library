from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

app_name = 'library'

urlpatterns = [
    path('', views.BookListView.as_view(), name='book_list'),
    path('book/<slug:slug>/', views.BookDetailView.as_view(), name='book_detail'),
    path('genre/<slug:genre_slug>/', views.BookListView.as_view(), name='book_list_by_genre'),
    path('selection/', views.SelectionDetailView.as_view(), name='selection_detail'),
    path('selection/add/<slug:book_slug>/', views.AddToSelectionView.as_view(), name='add_to_selection'),
    path('selection/remove/<int:book_id>/', views.RemoveFromSelectionView.as_view(), name='remove_from_selection'),
    path('selection/clear/', views.ClearSelectionView.as_view(), name='clear_selection'),
    path('create-genre/', views.CreateGenreView.as_view(), name='create_genre'),
    path('create-book/', views.CreateBookView.as_view(), name='create_book'),
    path('create-loan/', views.CreateLoanView.as_view(), name='create_loan'),
    path('loans/', views.LoanListView.as_view(), name='loan_list'),
    path('loan/success/<int:loan_id>/', views.LoanSuccessView.as_view(), name='loan_success'),
    path('loan/return/<int:loan_id>/', views.ReturnLoanView.as_view(), name='return_loan'),
    path('delete-book/<slug:slug>/', views.DeleteBookView.as_view(), name='delete_book'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='library:book_list'), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
]