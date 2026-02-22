from rest_framework import serializers
from .models import Category, Transaction,Account, AccountHistory
from datetime import date


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'type']
        
class TransactionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    

    class Meta:
        model = Transaction
        fields = ['id', 'description', 'value', 'date', 'category', 'category_name']
        
class AccountHistorySerializer(serializers.ModelSerializer):
    value = serializers.DecimalField(source='operation_value', max_digits=12, decimal_places=2)
    end_value = serializers.DecimalField(source='value', max_digits=12, decimal_places=2, read_only=True)
    monthly_variation = serializers.DecimalField(source='calculated_variation', max_digits=12, decimal_places=2, read_only=True)
    account_name = serializers.CharField(source='account.name', read_only=True)
    
    class Meta:
        model = AccountHistory
        fields = ['id', 'account', 'account_name', 'value', 'end_value', 'type', 'date', 'monthly_variation', 'description']
    
    def validate(self, data):
        
        if not self.instance:
            account = data.get('account')
            #value = data.get('value')
            operation_value = data.get('operation_value')
            type_ = data.get('type')
            
            if not account.is_active:
                raise serializers.ValidationError({"account": "Não é possível adicionar histórico a uma conta inativa."})
            
            last_record = AccountHistory.objects.filter(account=account).order_by('-date', '-id').first()
            current_balance = last_record.value if last_record else 0
            
            if type_ == 'I':
                raise serializers.ValidationError({"type": "O tipo 'Início' (I) não pode ser criado manualmente. Ele é gerado automaticamente ao criar uma nova conta com um saldo inicial."})

            if type_ =='W' and operation_value >= 0:
                raise serializers.ValidationError({"value": f"Para retiradas (W), o valor deve ser negativo. Valor enviado: {operation_value}"})
            
            if type_ in ['A', 'R'] and operation_value <= 0:
                raise serializers.ValidationError({"value": f"Para Aportes (A) e Rendimentos (R), o valor deve ser positivo. Valor enviado: {operation_value}"})
            
            if type_ == 'E':
                raise serializers.ValidationError({"type": "Para encerrar uma conta, utilize o endpoint específico: POST /api/accounts/{id}/close/"})
            
            if type_ == 'V':
                raise serializers.ValidationError({"type": "Para reativar uma conta, utilize o endpoint específico: POST /api/accounts/{id}/reactivate/"})
            
            
            new_balance = current_balance + operation_value
            
            if new_balance < 0:
                raise serializers.ValidationError({"value": "Saldo insuficiente. Saldo atual: R${:.2f}".format(current_balance)})
            
            data['value'] = new_balance
        return data




class AccountSerializer(serializers.ModelSerializer):
    current_balance = serializers.SerializerMethodField()
    total_yield = serializers.SerializerMethodField()
    initial_value = serializers.DecimalField(max_digits=12, decimal_places=2, write_only=True, required=False)
    
    class Meta:
        model = Account
        fields = ['id', 'name', 'is_active', 'current_balance', 'total_yield', 'initial_value']
        
    def get_current_balance(self, obj):
        # The history is prefetched and ordered chronologically ('date', 'id') in the ViewSet.
        # The last item in the prefetched list is the latest record.
        # Accessing .all() uses the prefetched cache.
        history_list = list(obj.history.all())
        if history_list:
            return history_list[-1].value
        return 0
    
    def get_total_yield(self, obj):
        """
        Calcula o rendimento total da conta somando as variações de todos os registros de histórico do tipo 'R' (Rendimento).
        Usa o histórico pré-carregado (prefetched) para evitar N+1 queries.
        """
        # The history is prefetched and ordered by ('date', 'id') in the view's get_queryset
        all_history = list(obj.history.all())

        if not all_history:
            return 0

        total_yield = 0
        previous_value = 0
        for record in all_history:
            variation = record.value - previous_value
            if record.type == 'R':
                total_yield += variation
            previous_value = record.value
        return total_yield

    def validate_initial_value(self, value):
        if value < 0:
            raise serializers.ValidationError("O saldo inicial nao pode ser negativo.")
        return value
    
    def create(self, validated_data):
        initial_value = validated_data.pop('initial_value', 0)
        account = Account.objects.create(**validated_data)
        
        if initial_value:
            #AccountHistory.objects.create(account=account, value=initial_value, type='I', date=date.today(), description='Saldo Inicial')
            AccountHistory.objects.create(
                account=account,
                value = initial_value, #saldo final
                operation_value = initial_value, #valor da operação
                type='I',
                date = date.today(),
                description='Saldo Inicial'
            )
        return account