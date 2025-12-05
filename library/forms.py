from django import forms
from .models import Genre, Book, Reader
from datetime import datetime
from django.utils.text import slugify
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class GenreForm(forms.ModelForm):
    class Meta:
        model = Genre
        fields = ['name', 'slug']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Nombre del género',
                'required': True
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'URL amigable (ej: ciencia-ficcion)',
                'required': True
            }),
        }


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'genre', 'publication_year', 'available']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Título del libro',
                'required': True
            }),
            'author': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Nombre del autor',
                'required': True
            }),
            'genre': forms.Select(attrs={
                'class': 'form-input',
                'required': True
            }),
            'publication_year': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': f'Ej: {datetime.now().year}',
                'required': True,
                'min': '1000',
                'max': '2100',
                'value': datetime.now().year
            }),
            'available': forms.CheckboxInput(attrs={
                'class': 'form-checkbox',
            }),
        }
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        slug = slugify(title)
        
        # Verificar si ya existe un libro con este slug
        if Book.objects.filter(slug=slug).exists():
            raise forms.ValidationError(
                f'Ya existe un libro con un título similar. Por favor, usa un título diferente.'
            )
        return title
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.slug:
            instance.slug = slugify(instance.title)
        if commit:
            instance.save()
        return instance


class ReaderForm(forms.ModelForm):
    class Meta:
        model = Reader
        fields = ['name', 'email']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ej: Juan Pérez García',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ej: juan.perez@ejemplo.com',
                'required': True
            }),
        }


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-input',
        'placeholder': 'correo@ejemplo.com'
    }))
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Nombre de usuario'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Contraseña'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Confirmar contraseña'
        })