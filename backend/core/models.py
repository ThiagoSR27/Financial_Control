from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    TYPE_CHOICES = [
        ('R', 'Receita'),
        ('D', 'Despesa'),
    ]
    type = models.CharField(max_length=1, choices=TYPE_CHOICES, default= 'D')
    
    def __str__(self):
        return self.name

class Transaction(models.Model):
    description = models.CharField(max_length=255)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    #Optional: Vincular a um usuario
    #user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.description} - R${self.value}"

    class Meta:
        ordering = ['-date']

class Account(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
class AccountHistory(models.Model):
    TYPE_CHOICES = [
        ('I', 'Inicio'),
        ('R', 'Rendimento'),
        ('A', 'Aporte'),
        ('W', 'Retirada'),
        ('E', 'Encerrada'),
        ('V', 'Reativação'),
    ]
    
    account = models.ForeignKey(Account, related_name='history', on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=12, decimal_places=2, help_text="Saldo Atual")
    operation_value = models.DecimalField(max_digits=12, decimal_places = 2, default = 0)
    date = models.DateField()
    type = models.CharField(max_length=1, choices=TYPE_CHOICES)
    description = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        ordering = ['-date']
        
    def save(self, *args, **kwargs):
        #If marked as Encerrada, set account to inactive
        if self.type == 'E':
            self.account.is_active = False
            self.account.save()
        super().save(*args, **kwargs)

    def clean(self):
        # Validação que funciona no Admin e na API
        if self.type == 'I' and self.value < 0:
            raise ValidationError({'value': "O saldo inicial não pode ser negativo."})
        # Nota: Não validamos 'W' aqui porque no Banco salvamos o Saldo Final, 
        # que pode ser positivo mesmo após uma retirada.