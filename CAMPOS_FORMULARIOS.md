# 📋 Referência de Campos dos Formulários - PDV System

Este documento lista todos os campos (name attributes) dos formulários e sua correspondência com os modelos do Django.

## 🏷️ Product (Produto)

### Formulário: Adicionar/Editar Produto
```html
<input name="code" />              <!-- CharField: Código do produto -->
<input name="name" />              <!-- CharField: Nome do produto -->
<textarea name="description" />    <!-- TextField: Descrição -->
<select name="category" />         <!-- ForeignKey: Category -->
<select name="unit_of_measure" /> <!-- ForeignKey: UnitOfMeasure -->
<input name="unit_price" />        <!-- DecimalField: Preço unitário -->
<input name="cost_price" />        <!-- DecimalField: Preço de custo -->
<input name="barcode" />           <!-- CharField: Código de barras -->
<input name="stock_quantity" />    <!-- DecimalField: Quantidade em estoque -->
<input name="minimum_stock" />     <!-- DecimalField: Estoque mínimo -->
<input name="image" />             <!-- ImageField: Imagem do produto -->
<input name="is_active" />         <!-- BooleanField: Ativo -->
<input name="allows_bulk_sale" />  <!-- BooleanField: Permite venda avulsa -->
```

### Modelo Correspondente
```python
class Product(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    unit_of_measure = models.ForeignKey(UnitOfMeasure, on_delete=models.PROTECT, related_name='products')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_quantity = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    minimum_stock = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    allows_bulk_sale = models.BooleanField(default=True)
    barcode = models.CharField(max_length=100, blank=True, unique=True, null=True)
    image = models.ImageField(upload_to='products/%Y/%m/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
```

---

## 👤 Customer (Cliente)

### Formulário: Cadastrar Cliente
```html
<input name="full_name" />     <!-- CharField: Nome completo -->
<input name="phone" />         <!-- CharField: Telefone -->
<input name="email" />         <!-- EmailField: E-mail -->
<input name="cpf" />           <!-- CharField: CPF -->
<textarea name="address" />    <!-- TextField: Endereço -->
<textarea name="notes" />      <!-- TextField: Observações -->
<input name="is_active" />     <!-- BooleanField: Ativo -->
```

### Modelo Correspondente
```python
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='customer')
    full_name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    cpf = models.CharField(max_length=14, blank=True, unique=True, null=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
```

---

## 💰 Sale (Venda)

### Formulário: Nova Venda
```html
<input name="customer" />          <!-- ForeignKey: Customer (opcional) -->
<select name="payment_method" />   <!-- CharField: Método de pagamento -->
<input name="discount" />          <!-- DecimalField: Desconto -->
<input name="amount_paid" />       <!-- DecimalField: Valor pago -->
<textarea name="notes" />          <!-- TextField: Observações -->
```

### Valores de payment_method
- `CASH` - Dinheiro
- `DEBIT` - Débito
- `CREDIT` - Crédito
- `PIX` - PIX
- `TRANSFER` - Transferência

### Modelo Correspondente
```python
class Sale(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Dinheiro'),
        ('DEBIT', 'Débito'),
        ('CREDIT', 'Crédito'),
        ('PIX', 'PIX'),
        ('TRANSFER', 'Transferência'),
    ]
    
    seller = models.ForeignKey(User, on_delete=models.PROTECT, related_name='sales')
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    change_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
```

---

## 📦 Order (Pedido)

### Formulário: Novo Pedido
```html
<input name="customer" />          <!-- ForeignKey: Customer -->
<select name="payment_method" />   <!-- CharField: Método de pagamento -->
<input name="payment_proof" />     <!-- FileField: Comprovante de pagamento -->
<input name="discount" />          <!-- DecimalField: Desconto -->
<textarea name="notes" />          <!-- TextField: Observações -->
```

### Valores de status
- `PENDING` - Pendente (padrão)
- `PAYMENT_UPLOADED` - Comprovante Enviado
- `CONFIRMED` - Confirmado
- `PROCESSING` - Em Processamento
- `READY` - Pronto para Retirada
- `COMPLETED` - Concluído
- `CANCELLED` - Cancelado

### Modelo Correspondente
```python
class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pendente'),
        ('PAYMENT_UPLOADED', 'Comprovante Enviado'),
        ('CONFIRMED', 'Confirmado'),
        ('PROCESSING', 'Em Processamento'),
        ('READY', 'Pronto para Retirada'),
        ('COMPLETED', 'Concluído'),
        ('CANCELLED', 'Cancelado'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Dinheiro'),
        ('DEBIT', 'Débito'),
        ('CREDIT', 'Crédito'),
        ('PIX', 'PIX'),
        ('TRANSFER', 'Transferência'),
    ]
    
    order_code = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_proof = models.FileField(upload_to='payment_proofs/%Y/%m/%d/', blank=True, null=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
```

---

## 📝 Itens (SaleItem / OrderItem)

### Campos comuns para itens
```html
<input name="product" />      <!-- ForeignKey: Product -->
<input name="quantity" />     <!-- DecimalField: Quantidade -->
<input name="unit_price" />   <!-- DecimalField: Preço unitário -->
<input name="notes" />        <!-- TextField: Observações -->
```

### Modelos
```python
class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='sale_items')
    quantity = models.DecimalField(max_digits=10, decimal_places=3)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)  # Calculado automaticamente
    notes = models.TextField(blank=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_items')
    quantity = models.DecimalField(max_digits=10, decimal_places=3)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)  # Calculado automaticamente
    notes = models.TextField(blank=True)
```

---

## 📊 Category (Categoria)

### Formulário
```html
<input name="name" />             <!-- CharField: Nome -->
<textarea name="description" />   <!-- TextField: Descrição -->
<input name="is_active" />        <!-- BooleanField: Ativo -->
```

### Modelo
```python
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
```

---

## 📏 UnitOfMeasure (Unidade de Medida)

### Formulário
```html
<input name="name" />                    <!-- CharField: Nome -->
<input name="abbreviation" />            <!-- CharField: Abreviação -->
<select name="unit_type" />              <!-- CharField: Tipo de unidade -->
<input name="base_unit_conversion" />    <!-- DecimalField: Conversão -->
<input name="allows_fraction" />         <!-- BooleanField: Permite fração -->
<input name="is_active" />               <!-- BooleanField: Ativo -->
```

### Valores de unit_type
- `WEIGHT` - Peso
- `VOLUME` - Volume
- `UNIT` - Unidade
- `PACKAGE` - Embalagem

### Modelo
```python
class UnitOfMeasure(models.Model):
    UNIT_TYPE_CHOICES = [
        ('WEIGHT', 'Peso'),
        ('VOLUME', 'Volume'),
        ('UNIT', 'Unidade'),
        ('PACKAGE', 'Embalagem'),
    ]
    
    name = models.CharField(max_length=50, unique=True)
    abbreviation = models.CharField(max_length=10, unique=True)
    unit_type = models.CharField(max_length=20, choices=UNIT_TYPE_CHOICES)
    base_unit_conversion = models.DecimalField(max_digits=10, decimal_places=4, default=1.0)
    allows_fraction = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
```

---

## 🔐 UserProfile (Perfil de Usuário)

### Formulário
```html
<select name="user" />           <!-- OneToOneField: User -->
<select name="role" />           <!-- CharField: Função -->
<input name="phone" />           <!-- CharField: Telefone -->
<textarea name="address" />      <!-- TextField: Endereço -->
<input name="cpf" />             <!-- CharField: CPF -->
<input name="birth_date" />      <!-- DateField: Data de nascimento -->
<input name="avatar" />          <!-- ImageField: Avatar -->
<input name="is_active" />       <!-- BooleanField: Ativo -->
```

### Valores de role
- `ADMIN` - Administrador
- `MANAGER` - Gerente
- `SELLER` - Vendedor
- `CUSTOMER` - Cliente

### Modelo
```python
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('MANAGER', 'Gerente'),
        ('SELLER', 'Vendedor'),
        ('CUSTOMER', 'Cliente'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CUSTOMER')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    cpf = models.CharField(max_length=14, blank=True, unique=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/%Y/%m/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
```

---

## 💡 Dicas de Implementação

### 1. Validação no Frontend
```javascript
// Exemplo de validação de CPF
function validateCPF(cpf) {
    // Implementação no main.js
}

// Exemplo de formatação de moeda
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}
```

### 2. Processamento no Backend (views.py)
```python
from django.shortcuts import render, redirect
from .models import Product, Sale, SaleItem

def create_sale(request):
    if request.method == 'POST':
        # Capturar dados do formulário
        customer_id = request.POST.get('customer')
        payment_method = request.POST.get('payment_method')
        discount = request.POST.get('discount', 0)
        amount_paid = request.POST.get('amount_paid')
        notes = request.POST.get('notes', '')
        
        # Criar venda
        sale = Sale.objects.create(
            seller=request.user,
            customer_id=customer_id if customer_id else None,
            payment_method=payment_method,
            discount=discount,
            amount_paid=amount_paid,
            notes=notes
        )
        
        # Adicionar itens...
        
        return redirect('sale_success', sale_id=sale.id)
    
    return render(request, 'nova_venda.html')
```

### 3. CSRF Token
**Importante:** Sempre inclua o CSRF token em formulários POST
```html
<form method="POST" action="#">
    {% csrf_token %}
    <!-- Seus campos aqui -->
</form>
```

### 4. Upload de Arquivos
Para formulários com upload de arquivos:
```html
<form method="POST" action="#" enctype="multipart/form-data">
    {% csrf_token %}
    <input type="file" name="image" />
</form>
```

---

## 📌 Notas Importantes

1. **Campos Obrigatórios**: Campos marcados com `required` no HTML devem ser validados também no backend
2. **Campos Calculados**: Campos como `total_price`, `subtotal`, `change_amount` são calculados automaticamente pelos métodos `save()` dos modelos
3. **Relacionamentos**: Use o ID do objeto relacionado (ex: `category_id=1`) ou o objeto diretamente
4. **Decimais**: Use sempre ponto (.) como separador decimal, não vírgula
5. **Datas**: Formato esperado: `YYYY-MM-DD` (ex: 2025-11-13)
6. **Arquivos**: Certifique-se de que `MEDIA_ROOT` e `MEDIA_URL` estão configurados no `settings.py`

---

**Última atualização: 13/11/2025**
