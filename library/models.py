from django.db import models
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager

# Create your models here.
class Genre(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name
    
class Book(models.Model):
    title =  models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    publication_year = models.PositiveIntegerField()
    available = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return self.title

    @property
    def is_available(self):
        return self.available

class Reader(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()

    def active_loans(self):
        return Loan.objects.filter(reader=self, status='active').count()
    
    def last_loan(self):
        return Loan.objects.filter(reader=self).order_by('-created_at').first()
    
class Loan(models.Model):
    STATUS_CHOICES = [
        ('active', 'Activo'),
        ('returned', 'Devuelto'),
        ('late', 'Vencido'),
    ]  

    reader = models.ForeignKey(Reader, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    if TYPE_CHECKING:
        items: 'RelatedManager[LoanItem]'

    @property
    def is_active(self):
        return self.status == 'active'
    
    def total_books(self):
        return sum(item.quantity for item in self.items.all())
    
    def mark_returned(self):
        self.status = 'returned'
        self.save()

class LoanItem(models.Model):
    loan = models.ForeignKey(Loan, related_name='items', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.PROTECT)
    quantity = models.PositiveBigIntegerField(default=1)      

