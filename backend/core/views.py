from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Subquery, OuterRef, F, Window, DecimalField, ExpressionWrapper, Prefetch
from django.db.models.functions import Lag, Coalesce
from datetime import date
from .models import Category, Transaction,Account, AccountHistory
from .serializers import CategorySerializer, TransactionSerializer, AccountSerializer, AccountHistorySerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        #soma do total das receitas(caregory__type='R')
        total_income = Transaction.objects.filter(category__type='R').aggregate(Sum('value'))['value__sum'] or 0
        
        #soma do total das despesas(category__type='D')
        total_expense = Transaction.objects.filter(category__type='D').aggregate(Sum('value'))['value__sum'] or 0
        
        return Response({
            'income': total_income,
            'expenses': total_expense,
            'balance': total_income - total_expense

        })
    
class AccountViewSet(viewsets.ModelViewSet):
    queryset= Account.objects.filter(is_active=True)
    serializer_class = AccountSerializer
    
    def get_queryset(self):
        """Permite que ações específicas encontrem contas inativas."""
        if self.action in ['close', 'reactivate']:
            queryset = Account.objects.all()
        else:
            queryset = super().get_queryset()
        
        # Prefetch history in chronological order to optimize yield calculation in serializer
        return queryset.prefetch_related(
            Prefetch('history', queryset=AccountHistory.objects.order_by('date', 'id'))
        )
    
    @action(detail=False, methods=['get'])
    def total_wealth(self, request):
        """Calcula o total do patrimônio somando os saldos mais recentes de todas as contas ativas de forma otimizada."""
        # Subquery para encontrar o valor do último histórico de cada conta (OuterRef se refere à query principal de Account)
        latest_history_value = AccountHistory.objects.filter(
            account=OuterRef('pk')
        ).order_by('-date').values('value')[:1]

        # Agrega (soma) os valores anotados em uma única consulta
        total_data = Account.objects.filter(is_active=True).annotate(
            latest_value=Subquery(latest_history_value)
        ).aggregate(total=Sum('latest_value'))
        
        return Response({'total_wealth': total_data['total'] or 0})
    
    @action(detail = True, methods=['post'])
    def close(self, request, pk=None):
        """Encerra uma conta, criando um registro de encerramento no histórico com valor 0."""
        account = self.get_object()
        
        latest_history = account.history.first()
        current_balance = latest_history.value if latest_history else 0
        
        if current_balance !=0:
            return Response({'error': f'a conta nao pode ser encerrada ainda pois o saldo atual é de R${current_balance}. O saldo deve ser zero para encerrar a conta.'}, status=status.HTTP_400_BAD_REQUEST)
        
        AccountHistory.objects.create(
            account=account,
            value=0,
            type = 'E',
            date=date.today(),
            description='Encerramento de conta'
        )
        
        return Response({'status': f'A conta "{account.name}" foi encerrada com sucesso.'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def reactivate(self, request, pk=None):
        """Reativa uma conta inativa."""
        account = self.get_object()
        
        if account.is_active:
            return Response({'error': f'A conta "{account.name}" já está ativa.'}, status=status.HTTP_400_BAD_REQUEST)
        
        account.is_active = True
        account.save()
        
        AccountHistory.objects.create(account=account, value = 0, type='V', date=date.today(), description='Reativação de conta')
        
        return Response({'status': f'A conta "{account.name}" foi reativada com sucesso.'}, status=status.HTTP_200_OK)
    
class AccountHistoryViewSet(viewsets.ModelViewSet):
    #queryset = AccountHistory.objects.all()
    
    queryset = AccountHistory.objects.annotate(
        previous_value=Window(
            expression=Lag('value', default=0, output_field=DecimalField(max_digits=12, decimal_places=2)),
            partition_by=[F('account_id')],
            order_by=[F('date').asc(), F('id').asc()]
        )
    ).annotate(
        calculated_variation=ExpressionWrapper(F('value') - F('previous_value'), output_field=DecimalField(max_digits=12, decimal_places=2))
    ).order_by('-date', '-id')
    
    serializer_class = AccountHistorySerializer
    filterset_fields = ['account', 'type', 'date']