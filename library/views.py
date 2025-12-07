from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView, View, CreateView
from django.db.models import QuerySet
from typing import Any
from .models import Book, Genre, Reader, Loan, LoanItem
from .selection import LoanSelection
from .forms import GenreForm, BookForm, ReaderForm, CustomUserCreationForm
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login

# Create your views here.


SESSION_KEY = "loan_selection"


def get_selection(request):
    raw = request.session.get(SESSION_KEY)
    if raw:
        return LoanSelection.from_dict(raw)
    return LoanSelection()


def save_selection(request, selection):
    request.session[SESSION_KEY] = selection.to_dict()
    request.session.modified = True


class BaseLibraryView(TemplateView):
    extra_context = {"system_name": "Biblioteca Pública"}

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["genres"] = Genre.objects.all()
        return ctx


class GenreListMixin:
    kwargs: dict[str, Any]
    
    def get_queryset(self) -> QuerySet[Book]:
        qs = super().get_queryset()  # type: ignore
        slug = self.kwargs.get("genre_slug")
        if slug:
            qs = qs.filter(genre__slug=slug)
        return qs


class BookListView(GenreListMixin, ListView):
    model = Book
    template_name = "book_list.html"
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('library:login')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["genres"] = Genre.objects.all()
        ctx["system_name"] = "Biblioteca Pública"
        return ctx


class BookDetailView(DetailView):
    model = Book
    template_name = "book_detail.html"
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["genres"] = Genre.objects.all()
        ctx["system_name"] = "Biblioteca Pública"
        return ctx



# SELECCIÓN DE PRÉSTAMO

class AddToSelectionView(View):
    def post(self, request, book_slug):
        book = get_object_or_404(Book, slug=book_slug)
        
        # Solo agregar si el libro está disponible
        if book.available:
            selection = get_selection(request)
            selection.add_book(book)
            save_selection(request, selection)
            messages.success(request, f'Libro "{book.title}" agregado a tu selección')
        else:
            messages.warning(request, f'El libro "{book.title}" no está disponible')
        
        return redirect("library:selection_detail")


class RemoveFromSelectionView(View):
    def post(self, request, book_id):
        selection = get_selection(request)
        selection.remove_book(book_id)
        save_selection(request, selection)
        messages.info(request, 'Libro eliminado de tu selección')
        return redirect("library:selection_detail")


class ClearSelectionView(View):
    def post(self, request):
        selection = get_selection(request)
        selection.clear()
        save_selection(request, selection)
        messages.info(request, 'Selección limpiada')
        return redirect("library:selection_detail")


class SelectionDetailView(TemplateView):
    template_name = "loan_selection_detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["selection"] = get_selection(self.request)
        ctx["genres"] = Genre.objects.all()
        ctx["system_name"] = "Biblioteca Pública"
        return ctx    


# CREAR GÉNEROS Y LIBROS

class CreateGenreView(LoginRequiredMixin, CreateView):
    model = Genre
    form_class = GenreForm
    template_name = "create_genre.html"
    success_url = reverse_lazy("library:book_list")
    login_url = '/login/'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, 'No tienes permisos para crear géneros')
            return redirect('library:book_list')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["genres"] = Genre.objects.all()
        ctx["system_name"] = "Biblioteca Pública"
        return ctx
    
    def form_valid(self, form):
        messages.success(self.request, f'Género "{form.cleaned_data["name"]}" creado exitosamente!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        # Mostrar errores de validación como mensajes
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, str(error))
        return super().form_invalid(form)


class CreateBookView(LoginRequiredMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = "create_book.html"
    success_url = reverse_lazy("library:book_list")
    login_url = '/login/'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, 'No tienes permisos para crear libros')
            return redirect('library:book_list')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["genres"] = Genre.objects.all()
        ctx["system_name"] = "Biblioteca Pública"
        return ctx
    
    def form_valid(self, form):
        messages.success(self.request, f'Libro "{form.cleaned_data["title"]}" agregado al catálogo!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        # Mostrar errores de validación como mensajes
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, str(error))
        return super().form_invalid(form)


# PRÉSTAMOS

class CreateLoanView(CreateView):
    model = Reader
    form_class = ReaderForm
    template_name = "create_loan.html"
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["selection"] = get_selection(self.request)
        ctx["genres"] = Genre.objects.all()
        ctx["system_name"] = "Biblioteca Pública"
        return ctx
    
    def form_valid(self, form):
        # Obtener o crear el lector
        reader, created = Reader.objects.get_or_create(
            email=form.cleaned_data['email'],
            defaults={'name': form.cleaned_data['name']}
        )
        
        # Crear el préstamo
        loan = Loan.objects.create(reader=reader)
        loan_id = loan.pk  # type: int
        
        # Obtener la selección
        selection = get_selection(self.request)
        
        # Crear los items del préstamo
        for book_id, item in selection.items.items():
            book = Book.objects.get(id=book_id)
            LoanItem.objects.create(
                loan=loan,
                book=book,
                quantity=item.quantity
            )
            # Marcar libro como no disponible
            book.available = False
            book.save()
        
        # Limpiar la selección
        selection.clear()
        save_selection(self.request, selection)
        
        messages.success(self.request, f'¡Préstamo creado exitosamente para {reader.name}!')
        
        # Redirigir a página de éxito
        return redirect('library:loan_success', loan_id=loan_id)


class LoanSuccessView(DetailView):
    model = Loan
    template_name = "loan_success.html"
    pk_url_kwarg = 'loan_id'
    context_object_name = 'loan'
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["genres"] = Genre.objects.all()
        ctx["system_name"] = "Biblioteca Pública"
        return ctx


class LoanListView(LoginRequiredMixin, ListView):
    model = Loan
    template_name = "loan_list.html"
    context_object_name = "loans"
    login_url = '/login/'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, 'No tienes permisos para ver préstamos')
            return redirect('library:book_list')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return Loan.objects.all().order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["genres"] = Genre.objects.all()
        ctx["system_name"] = "Biblioteca Pública"
        return ctx


class ReturnLoanView(LoginRequiredMixin, View):
    login_url = '/login/'
    
    def post(self, request, loan_id):
        if not request.user.is_superuser:
            messages.error(request, 'No tienes permisos para marcar devoluciones')
            return redirect('library:book_list')
        
        loan = get_object_or_404(Loan, id=loan_id)
        
        if loan.status == 'returned':
            messages.warning(request, 'Este préstamo ya fue marcado como devuelto')
        else:
            # Marcar préstamo como devuelto
            loan.mark_returned()
            
            # Marcar todos los libros como disponibles nuevamente
            for item in loan.items.all():
                item.book.available = True
                item.book.save()
            
            messages.success(request, f'Préstamo devuelto exitosamente. Los libros están disponibles nuevamente.')
        
        return redirect('library:loan_list')


# ELIMINAR LIBROS

class DeleteBookView(LoginRequiredMixin, View):
    login_url = '/login/'
    
    def post(self, request, slug):
        if not request.user.is_superuser:
            messages.error(request, 'No tienes permisos para eliminar libros')
            return redirect('library:book_list')
        
        book = get_object_or_404(Book, slug=slug)
        
        active_loans = LoanItem.objects.filter(book=book, loan__status='active')
        if active_loans.exists():
            messages.error(request, f'No se puede eliminar "{book.title}" porque está en préstamos activos. Marca los préstamos como devueltos primero.')
            return redirect('library:book_list')
        
        returned_loan_items = LoanItem.objects.filter(book=book, loan__status='returned')
        returned_loan_items.delete()
        
        book_title = book.title
        book.delete()
        messages.success(request, f'Libro "{book_title}" eliminado exitosamente')
        return redirect('library:book_list')


# AUTENTICACIÓN

class CustomLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('library:book_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'¡Bienvenido {form.get_user().username}!')
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Usuario o contraseña incorrectos')
        return super().form_invalid(form)


class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'register.html'
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, f'¡Bienvenido {user.username}! Tu cuenta ha sido creada exitosamente')
        return redirect('library:book_list')
    
    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, str(error))
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["genres"] = Genre.objects.all()
        ctx["system_name"] = "Biblioteca Pública"
        return ctx