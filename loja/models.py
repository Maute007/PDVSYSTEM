"""
Models for PDV System - Complete Sales Management
Includes: Categories, Products, User Profiles, Orders, Sales, Reports, and Audit
"""
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, FileExtensionValidator
from django.utils import timezone
from django.db.models import Sum, F
from datetime import timedelta


class Category(models.Model):
    """
    Product Categories
    Organizes products into logical groups for better management
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nome'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Descrição'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativo'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em'
    )

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name


class UnitOfMeasure(models.Model):
    """
    Units of Measure for Products
    Supports weight, volume, units, and packages with conversion factors
    Examples: kg (1000g), g (1g), L (1000ml), unidade, caixa, pacote
    """
    UNIT_TYPE_CHOICES = [
        ('WEIGHT', 'Peso'),
        ('VOLUME', 'Pacote'),
        ('UNIT', 'Unidade'),
        ('PACKAGE', 'Embalagem'),
    ]

    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Nome'
    )
    abbreviation = models.CharField(
        max_length=10,
        unique=True,
        verbose_name='Abreviação'
    )
    unit_type = models.CharField(
        max_length=20,
        choices=UNIT_TYPE_CHOICES,
        verbose_name='Tipo de Unidade'
    )
    base_unit_conversion = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=1.0,
        validators=[MinValueValidator(Decimal('0.0001'))],
        verbose_name='Conversão para Unidade Base',
        help_text='Ex: 1 kg = 1000g (base_unit_conversion = 1000)'
    )
    allows_fraction = models.BooleanField(
        default=False,
        verbose_name='Permite Fração',
        help_text='Se verdadeiro, permite vender quantidades fracionadas (ex: 0.5 kg)'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativo'
    )

    class Meta:
        verbose_name = 'Unidade de Medida'
        verbose_name_plural = 'Unidades de Medida'
        ordering = ['name']
        indexes = [
            models.Index(fields=['abbreviation']),
            models.Index(fields=['unit_type']),
        ]

    def __str__(self):
        return f'{self.name} ({self.abbreviation})'


class Product(models.Model):
    """
    Product Stock Management
    Supports various unit types and dynamic pricing based on quantity
    """
    STOCK_STATUS_CHOICES = [
        ('IN_STOCK', 'Em Estoque'),
        ('LOW_STOCK', 'Estoque Baixo'),
        ('OUT_OF_STOCK', 'Sem Estoque'),
    ]

    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Código',
        help_text='Código único do produto (SKU)'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Nome'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Descrição'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name='Categoria'
    )
    unit_of_measure = models.ForeignKey(
        UnitOfMeasure,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name='Unidade de Medida'
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Preço Unitário',
        help_text='Preço por unidade de medida'
    )
    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=0,
        verbose_name='Preço de Custo'
    )
    stock_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=0,
        validators=[MinValueValidator(Decimal('0.000'))],
        verbose_name='Quantidade em Estoque'
    )
    minimum_stock = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=0,
        validators=[MinValueValidator(Decimal('0.000'))],
        verbose_name='Estoque Mínimo',
        help_text='Alerta quando o estoque estiver abaixo deste valor'
    )
    stock_status = models.CharField(
        max_length=20,
        choices=STOCK_STATUS_CHOICES,
        default='IN_STOCK',
        verbose_name='Status do Estoque'
    )
    allows_bulk_sale = models.BooleanField(
        default=True,
        verbose_name='Permite Venda Avulsa',
        help_text='Se verdadeiro, permite vender quantidades fracionadas'
    )
    barcode = models.CharField(
        max_length=100,
        blank=True,
        unique=True,
        null=True,
        verbose_name='Código de Barras'
    )
    image = models.ImageField(
        upload_to='products/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='Imagem'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativo'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em'
    )

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['name']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['stock_status']),
            models.Index(fields=['barcode']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f'{self.code} - {self.name}'

    def update_stock_status(self):
        """Update stock status based on current quantity"""
        if self.stock_quantity <= 0:
            self.stock_status = 'OUT_OF_STOCK'
        elif self.stock_quantity <= self.minimum_stock:
            self.stock_status = 'LOW_STOCK'
        else:
            self.stock_status = 'IN_STOCK'
        self.save(update_fields=['stock_status'])

    def has_sufficient_stock(self, quantity):
        """Check if there's enough stock for a given quantity"""
        return self.stock_quantity >= quantity

    def calculate_total_price(self, quantity):
        """Calculate total price for a given quantity"""
        return self.unit_price * Decimal(str(quantity))


class UserProfile(models.Model):
    """
    Extended User Profile
    Adds additional information to Django's built-in User model
    """
    ROLE_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('MANAGER', 'Gerente'),
        ('SELLER', 'Vendedor'),
        ('CUSTOMER', 'Cliente'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Usuário'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='CUSTOMER',
        verbose_name='Função'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Telefone'
    )
    address = models.TextField(
        blank=True,
        verbose_name='Endereço'
    )
    cpf = models.CharField(
        max_length=14,
        blank=True,
        unique=True,
        null=True,
        verbose_name='CPF'
    )
    birth_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Data de Nascimento'
    )
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='Avatar'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativo'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em'
    )

    class Meta:
        verbose_name = 'Perfil de Usuário'
        verbose_name_plural = 'Perfis de Usuário'
        ordering = ['user__username']
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['cpf']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username} - {self.get_role_display()}'

    def is_seller(self):
        """Check if user is a seller or higher"""
        return self.role in ['SELLER', 'MANAGER', 'ADMIN']

    def is_manager(self):
        """Check if user is a manager or higher"""
        return self.role in ['MANAGER', 'ADMIN']


class Customer(models.Model):
    """
    Customer Information
    Can be linked to a User account or be a guest customer
    """
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customer',
        verbose_name='Usuário'
    )
    full_name = models.CharField(
        max_length=200,
        verbose_name='Nome Completo'
    )
    email = models.EmailField(
        blank=True,
        verbose_name='E-mail'
    )
    phone = models.CharField(
        max_length=20,
        verbose_name='Telefone'
    )
    address = models.TextField(
        blank=True,
        verbose_name='Endereço'
    )
    cpf = models.CharField(
        max_length=14,
        blank=True,
        unique=True,
        null=True,
        verbose_name='CPF'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Observações'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Ativo'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em'
    )

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['full_name']
        indexes = [
            models.Index(fields=['full_name']),
            models.Index(fields=['phone']),
            models.Index(fields=['cpf']),
            models.Index(fields=['is_active']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return self.full_name

    def total_purchases(self):
        """Calculate total amount of all completed purchases"""
        return self.orders.filter(
            status='COMPLETED'
        ).aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0.00')


class Order(models.Model):
    """
    Customer Orders (Remote Orders)
    Customers can place orders remotely and upload payment proof
    """
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
        ('DEBIT', 'Mpesa'),
        ('CREDIT', 'M-kesh'),
        ('PIX', 'E-mola'),
        ('TRANSFER', 'Banco'),
    ]

    order_code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Código do Pedido',
        help_text='Código único fornecido ao cliente'
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name='Cliente'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDENTE',
        verbose_name='Status'
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name='Método de Pagamento'
    )
    payment_proof = models.FileField(
        upload_to='payment_proofs/%Y/%m/%d/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])],
        verbose_name='Comprovante de Pagamento'
    )
    payment_proof_uploaded_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Comprovante Enviado em'
    )
    confirmed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='confirmed_orders',
        verbose_name='Confirmado por'
    )
    confirmed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Confirmado em'
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Subtotal'
    )
    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Desconto'
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Valor Total'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Observações'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em'
    )

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_code']),
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f'Pedido {self.order_code} - {self.customer.full_name}'

    def save(self, *args, **kwargs):
        if not self.order_code:
            self.order_code = self.generate_order_code()
        self.calculate_total()
        super().save(*args, **kwargs)

    def generate_order_code(self):
        """Generate unique order code"""
        import random
        import string
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not Order.objects.filter(order_code=code).exists():
                return code

    def calculate_total(self):
        """Calculate order totals"""
        items = self.items.select_related('product')
        self.subtotal = sum(item.total_price for item in items)
        self.total_amount = self.subtotal - self.discount

    def confirm_payment(self, user):
        """Confirm payment and change status"""
        self.status = 'CONFIRMED'
        self.confirmed_by = user
        self.confirmed_at = timezone.now()
        self.save(update_fields=['status', 'confirmed_by', 'confirmed_at'])


class OrderItem(models.Model):
    """
    Items in an Order
    Links products to orders with quantities and prices
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Pedido'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='order_items',
        verbose_name='Produto'
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        verbose_name='Quantidade'
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Preço Unitário'
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Preço Total'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Observações'
    )

    class Meta:
        verbose_name = 'Item do Pedido'
        verbose_name_plural = 'Itens do Pedido'
        ordering = ['id']
        indexes = [
            models.Index(fields=['order', 'product']),
        ]

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'

    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)


class Sale(models.Model):
    """
    Direct Sales (In-Store)
    Records sales made directly at the store
    """
    STATUS_CHOICES = [
        ('COMPLETED', 'Concluído'),
        ('CANCELLED', 'Cancelado'),
        ('REFUNDED', 'Reembolsado'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Dinheiro'),
        ('DEBIT', 'Débito'),
        ('CREDIT', 'Crédito'),
        ('PIX', 'PIX'),
        ('TRANSFER', 'Transferência'),
    ]

    sale_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Número da Venda'
    )
    seller = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='sales',
        verbose_name='Vendedor'
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sales',
        verbose_name='Cliente'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='COMPLETED',
        verbose_name='Status'
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name='Método de Pagamento'
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Subtotal'
    )
    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Desconto'
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Valor Total'
    )
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Valor Pago'
    )
    change_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Troco'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Observações'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em'
    )

    class Meta:
        verbose_name = 'Venda'
        verbose_name_plural = 'Vendas'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sale_number']),
            models.Index(fields=['seller', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['customer', '-created_at']),
        ]

    def __str__(self):
        return f'Venda {self.sale_number} - {self.seller.get_full_name() or self.seller.username}'

    def save(self, *args, **kwargs):
        if not self.sale_number:
            self.sale_number = self.generate_sale_number()
        # Don't calculate total here - it will be done manually in views
        # because we need items to be saved first
        if self.pk:  # Only calculate if already saved (has primary key)
            self.calculate_total()
        self.change_amount = max(self.amount_paid - self.total_amount, Decimal('0.00'))
        super().save(*args, **kwargs)

    def generate_sale_number(self):
        """Generate unique sale number"""
        today = timezone.now()
        prefix = today.strftime('%Y%m%d')
        last_sale = Sale.objects.filter(
            sale_number__startswith=prefix
        ).order_by('-sale_number').first()
        
        if last_sale:
            last_number = int(last_sale.sale_number[-4:])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f'{prefix}{new_number:04d}'

    def calculate_total(self):
        """Calculate sale totals"""
        if self.pk:  # Only calculate if sale has been saved
            items = self.items.select_related('product')
            self.subtotal = sum(item.total_price for item in items)
            self.total_amount = self.subtotal - self.discount


class SaleItem(models.Model):
    """
    Items in a Sale
    Links products to sales with quantities and prices
    """
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Venda'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='sale_items',
        verbose_name='Produto'
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        verbose_name='Quantidade'
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Preço Unitário'
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Preço Total'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Observações'
    )

    class Meta:
        verbose_name = 'Item da Venda'
        verbose_name_plural = 'Itens da Venda'
        ordering = ['id']
        indexes = [
            models.Index(fields=['sale', 'product']),
        ]

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'

    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)


class WeeklySalesReport(models.Model):
    """
    Weekly Sales Report
    Automatically groups sales by week for analysis
    """
    year = models.IntegerField(
        verbose_name='Ano'
    )
    week_number = models.IntegerField(
        verbose_name='Número da Semana',
        help_text='Número da semana no ano (1-53)'
    )
    start_date = models.DateField(
        verbose_name='Data de Início'
    )
    end_date = models.DateField(
        verbose_name='Data de Término'
    )
    total_sales = models.IntegerField(
        default=0,
        verbose_name='Total de Vendas'
    )
    total_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Receita Total'
    )
    total_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Custo Total'
    )
    total_profit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Lucro Total'
    )
    total_orders = models.IntegerField(
        default=0,
        verbose_name='Total de Pedidos'
    )
    is_finalized = models.BooleanField(
        default=False,
        verbose_name='Finalizado',
        help_text='Relatório foi processado e finalizado'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em'
    )

    class Meta:
        verbose_name = 'Relatório Semanal de Vendas'
        verbose_name_plural = 'Relatórios Semanais de Vendas'
        ordering = ['-year', '-week_number']
        unique_together = [['year', 'week_number']]
        indexes = [
            models.Index(fields=['year', 'week_number']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['is_finalized']),
        ]

    def __str__(self):
        return f'Semana {self.week_number}/{self.year} ({self.start_date} a {self.end_date})'

    @classmethod
    def generate_report(cls, date=None):
        """Generate or update weekly report for a given date"""
        if date is None:
            date = timezone.now().date()
        
        # Get week information
        year = date.isocalendar()[0]
        week_number = date.isocalendar()[1]
        
        # Calculate week start and end
        week_start = date - timedelta(days=date.weekday())
        week_end = week_start + timedelta(days=6)
        
        # Get or create report
        report, created = cls.objects.get_or_create(
            year=year,
            week_number=week_number,
            defaults={
                'start_date': week_start,
                'end_date': week_end,
            }
        )
        
        # Calculate sales statistics
        sales = Sale.objects.filter(
            created_at__date__gte=week_start,
            created_at__date__lte=week_end,
            status='COMPLETED'
        ).select_related('seller').prefetch_related('items__product')
        
        orders = Order.objects.filter(
            created_at__date__gte=week_start,
            created_at__date__lte=week_end,
            status='COMPLETED'
        ).select_related('customer').prefetch_related('items__product')
        
        # Calculate totals
        total_revenue = sum(sale.total_amount for sale in sales) + \
                       sum(order.total_amount for order in orders)
        
        total_cost = Decimal('0.00')
        for sale in sales:
            for item in sale.items.all():
                total_cost += item.product.cost_price * item.quantity
        
        for order in orders:
            for item in order.items.all():
                total_cost += item.product.cost_price * item.quantity
        
        report.total_sales = sales.count()
        report.total_orders = orders.count()
        report.total_revenue = total_revenue
        report.total_cost = total_cost
        report.total_profit = total_revenue - total_cost
        report.save()
        
        return report


class SellerPerformance(models.Model):
    """
    Seller Performance Tracking
    Tracks individual seller performance per week
    """
    weekly_report = models.ForeignKey(
        WeeklySalesReport,
        on_delete=models.CASCADE,
        related_name='seller_performances',
        verbose_name='Relatório Semanal'
    )
    seller = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='performances',
        verbose_name='Vendedor'
    )
    total_sales = models.IntegerField(
        default=0,
        verbose_name='Total de Vendas'
    )
    total_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Receita Total'
    )
    total_items_sold = models.IntegerField(
        default=0,
        verbose_name='Total de Itens Vendidos'
    )
    average_sale_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Valor Médio de Venda'
    )

    class Meta:
        verbose_name = 'Desempenho do Vendedor'
        verbose_name_plural = 'Desempenhos dos Vendedores'
        ordering = ['-total_revenue']
        unique_together = [['weekly_report', 'seller']]
        indexes = [
            models.Index(fields=['weekly_report', 'seller']),
            models.Index(fields=['seller', '-total_revenue']),
        ]

    def __str__(self):
        return f'{self.seller.get_full_name() or self.seller.username} - Semana {self.weekly_report.week_number}/{self.weekly_report.year}'


class AuditLog(models.Model):
    """
    Audit Trail
    Tracks all important actions in the system
    """
    ACTION_CHOICES = [
        ('CREATE', 'Criação'),
        ('UPDATE', 'Atualização'),
        ('DELETE', 'Exclusão'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('PAYMENT_CONFIRM', 'Confirmação de Pagamento'),
        ('SALE_COMPLETE', 'Venda Concluída'),
        ('SALE_CANCEL', 'Venda Cancelada'),
        ('ORDER_CREATE', 'Pedido Criado'),
        ('ORDER_CONFIRM', 'Pedido Confirmado'),
        ('STOCK_UPDATE', 'Atualização de Estoque'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs',
        verbose_name='Usuário'
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name='Ação'
    )
    model_name = models.CharField(
        max_length=100,
        verbose_name='Modelo',
        help_text='Nome do modelo afetado'
    )
    object_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='ID do Objeto'
    )
    description = models.TextField(
        verbose_name='Descrição'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='Endereço IP'
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name='User Agent'
    )
    device_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Tipo de Dispositivo',
        help_text='Desktop, Mobile, Tablet'
    )
    device_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Nome do Dispositivo'
    )
    browser = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Navegador'
    )
    sale_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Número da Venda',
        help_text='Número da venda relacionada'
    )
    product_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Preço do Produto',
        help_text='Preço no momento da ação'
    )
    product_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Nome do Produto'
    )
    changes = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Alterações',
        help_text='JSON com as alterações realizadas'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )

    class Meta:
        verbose_name = 'Log de Auditoria'
        verbose_name_plural = 'Logs de Auditoria'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action', '-created_at']),
            models.Index(fields=['model_name', 'object_id']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        user_name = self.user.get_full_name() or self.user.username if self.user else 'Sistema'
        return f'{user_name} - {self.get_action_display()} - {self.model_name} ({self.created_at.strftime("%d/%m/%Y %H:%M")})'

    @classmethod
    def log_action(cls, user, action, model_name, object_id=None, description='', ip_address=None, user_agent='', 
                   device_type='', device_name='', browser='', sale_number='', product_price=None, product_name='', changes=None):
        """Create an audit log entry"""
        return cls.objects.create(
            user=user,
            action=action,
            model_name=model_name,
            object_id=object_id,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            device_type=device_type,
            device_name=device_name,
            browser=browser,
            sale_number=sale_number,
            product_price=product_price,
            product_name=product_name,
            changes=changes
        )


class Notification(models.Model):
    """
    User Notifications
    System notifications for important events
    """
    NOTIFICATION_TYPE_CHOICES = [
        ('SALE_MILESTONE', 'Marco de Vendas'),
        ('PRODUCT_ADDED', 'Produto Adicionado'),
        ('LOW_STOCK', 'Estoque Baixo'),
        ('OUT_OF_STOCK', 'Sem Estoque'),
        ('ORDER_RECEIVED', 'Pedido Recebido'),
        ('ORDER_CONFIRMED', 'Pedido Confirmado'),
        ('PAYMENT_UPLOADED', 'Comprovante Enviado'),
        ('STOCK_UPDATED', 'Estoque Atualizado'),
    ]
    
    ICON_CHOICES = {
        'SALE_MILESTONE': 'bi-trophy-fill',
        'PRODUCT_ADDED': 'bi-box-seam-fill',
        'LOW_STOCK': 'bi-exclamation-triangle-fill',
        'OUT_OF_STOCK': 'bi-x-circle-fill',
        'ORDER_RECEIVED': 'bi-bell-fill',
        'ORDER_CONFIRMED': 'bi-check-circle-fill',
        'PAYMENT_UPLOADED': 'bi-file-earmark-check-fill',
        'STOCK_UPDATED': 'bi-arrow-repeat',
    }
    
    COLOR_CHOICES = {
        'SALE_MILESTONE': 'success',
        'PRODUCT_ADDED': 'primary',
        'LOW_STOCK': 'warning',
        'OUT_OF_STOCK': 'danger',
        'ORDER_RECEIVED': 'info',
        'ORDER_CONFIRMED': 'success',
        'PAYMENT_UPLOADED': 'info',
        'STOCK_UPDATED': 'primary',
    }
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Usuário'
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPE_CHOICES,
        verbose_name='Tipo'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Título'
    )
    message = models.TextField(
        verbose_name='Mensagem'
    )
    link = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Link',
        help_text='URL para o elemento relacionado'
    )
    related_object_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Tipo do Objeto'
    )
    related_object_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='ID do Objeto'
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name='Lida'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criada em'
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Lida em'
    )
    
    class Meta:
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f'{self.user.username} - {self.title}'
    
    def get_icon(self):
        """Get icon class for notification type"""
        return self.ICON_CHOICES.get(self.notification_type, 'bi-bell-fill')
    
    def get_color(self):
        """Get color class for notification type"""
        return self.COLOR_CHOICES.get(self.notification_type, 'primary')
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
    
    @classmethod
    def create_notification(cls, user, notification_type, title, message, link='', related_object_type='', related_object_id=None):
        """Create a new notification"""
        return cls.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            link=link,
            related_object_type=related_object_type,
            related_object_id=related_object_id
        )
    
    @classmethod
    def notify_sales_milestone(cls, user, count):
        """Notify when sales milestone is reached"""
        if count % 50 == 0:  # Every 50 sales
            return cls.create_notification(
                user=user,
                notification_type='SALE_MILESTONE',
                title=f'🎉 Marco de {count} Vendas Atingido!',
                message=f'Parabéns! Você atingiu {count} vendas. Continue o ótimo trabalho!',
                link='/relatorios/',
                related_object_type='SalesMilestone',
                related_object_id=count
            )
    
    @classmethod
    def notify_product_added(cls, user, product):
        """Notify when product is added"""
        return cls.create_notification(
            user=user,
            notification_type='PRODUCT_ADDED',
            title='Novo Produto Adicionado',
            message=f'O produto "{product.name}" foi adicionado ao sistema com sucesso.',
            link=f'/produtos/?search={product.code}',
            related_object_type='Product',
            related_object_id=product.id
        )
    
    @classmethod
    def notify_low_stock(cls, user, product):
        """Notify when product stock is low"""
        return cls.create_notification(
            user=user,
            notification_type='LOW_STOCK',
            title='⚠️ Estoque Baixo',
            message=f'O produto "{product.name}" está com estoque baixo ({product.stock_quantity} {product.unit_of_measure.abbreviation}). Reposição necessária!',
            link=f'/produtos/?search={product.code}',
            related_object_type='Product',
            related_object_id=product.id
        )
    
    @classmethod
    def notify_out_of_stock(cls, user, product):
        """Notify when product is out of stock"""
        return cls.create_notification(
            user=user,
            notification_type='OUT_OF_STOCK',
            title='❌ Produto Esgotado',
            message=f'O produto "{product.name}" está sem estoque. Reposição urgente!',
            link=f'/produtos/?search={product.code}',
            related_object_type='Product',
            related_object_id=product.id
        )
    
    @classmethod
    def notify_order_received(cls, user, order):
        """Notify when new order is received"""
        return cls.create_notification(
            user=user,
            notification_type='ORDER_RECEIVED',
            title='Novo Pedido Recebido',
            message=f'Pedido #{order.order_code} de {order.customer.full_name} (Total: {order.total_amount} Kz)',
            link=f'/pedidos/?search={order.order_code}',
            related_object_type='Order',
            related_object_id=order.id
        )
