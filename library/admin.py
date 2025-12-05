from django.contrib import admin
from .models import Genre, Book, Reader, Loan, LoanItem

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'genre', 'publication_year', 'available')
    list_filter = ('genre', 'available', 'publication_year')
    search_fields = ('title', 'author')

@admin.register(Reader)
class ReaderAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')
    search_fields = ('name', 'email')

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('reader', 'created_at', 'status')
    list_filter = ('status', 'created_at')
    search_fields = ('reader__name',)

@admin.register(LoanItem)
class LoanItemAdmin(admin.ModelAdmin):
    list_display = ('loan', 'book', 'quantity')
    search_fields = ('book__title',)
