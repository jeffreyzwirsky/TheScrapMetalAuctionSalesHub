# SMASH Marketplace - Complete Models File
# File: auctions/models.py
# Replace your existing models.py with this complete version

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

# ============================================
# PACKAGE MODEL - Groups Catalytic Converters
# ============================================

class Package(models.Model):
    """Groups catalytic converters into packages for sale"""
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='packages',
        help_text="User who owns this package"
    )
    name = models.CharField(
        max_length=200, 
        help_text="Package name (e.g., 'November Batch 1')"
    )
    
    STATUS_CHOICES = [
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('IN_SALE', 'In Sale'),
        ('SOLD', 'Sold')
    ]
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='IN_PROGRESS'
    )
    
    final_weight = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Total weight in pounds"
    )
    
    current_package_bid = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Sum of all item bids in this package"
    )
    
    notes = models.TextField(blank=True, help_text="Internal notes")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Package'
        verbose_name_plural = 'Packages'
    
    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"
    
    @property
    def item_count(self):
        """Count of catalytic converters in this package"""
        return self.products.count()
    
    @property
    def total_bids(self):
        """Total number of bids on all items in package"""
        return sum(item.bids.count() for item in self.products.all())


# ============================================
# SALE MODEL - Groups Packages into LOTs
# ============================================

class Sale(models.Model):
    """Groups packages into a sale/LOT for auction"""
    lot_number = models.CharField(
        max_length=50, 
        unique=True,
        help_text="e.g., LOT-2025-001"
    )
    
    packages = models.ManyToManyField(
        Package, 
        related_name='sales',
        help_text="Packages included in this sale"
    )
    
    # Sale Information
    title = models.CharField(max_length=200, help_text="Sale title for buyers")
    description = models.TextField(help_text="Detailed sale description")
    
    # Location & Logistics
    zip_code = models.CharField(
        max_length=10, 
        help_text="Pickup location ZIP code"
    )
    pickup_instructions = models.TextField(
        blank=True,
        help_text="How buyers should arrange pickup"
    )
    
    # Sale Details
    unit_count = models.IntegerField(
        help_text="Total number of catalytic converters"
    )
    total_weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total weight in pounds"
    )
    
    bid_due_date = models.DateTimeField(help_text="Bidding deadline")
    
    SELLER_TYPE_CHOICES = [
        ('GENERATOR', 'Generator'),
        ('PROCESSOR', 'Processor'),
        ('BROKER', 'Broker')
    ]
    seller_type = models.CharField(
        max_length=20, 
        choices=SELLER_TYPE_CHOICES
    )
    
    # Status
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('ACTIVE', 'Active'),
        ('BIDDING_CLOSED', 'Bidding Closed'),
        ('COMPLETED', 'Completed')
    ]
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='DRAFT'
    )
    
    # Bidding
    current_sale_bid = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Sum of all package bids"
    )
    
    winning_bid = models.ForeignKey(
        'Bid',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='won_sale'
    )
    
    # Watch Feature
    watchers = models.ManyToManyField(
        User, 
        related_name='watched_sales', 
        blank=True
    )
    
    # Seller
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sales'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Sale (LOT)'
        verbose_name_plural = 'Sales (LOTs)'
    
    def __str__(self):
        return f"{self.lot_number} - {self.title}"
    
    def get_absolute_url(self):
        return reverse('sale_detail', kwargs={'pk': self.pk})
    
    @property
    def is_active(self):
        """Check if sale is currently accepting bids"""
        return (
            self.status == 'ACTIVE' and 
            self.bid_due_date > timezone.now()
        )
    
    @property
    def total_packages(self):
        """Count of packages in this sale"""
        return self.packages.count()
    
    @property
    def total_items(self):
        """Count of all items across all packages"""
        return sum(pkg.item_count for pkg in self.packages.all())


# ============================================
# CATEGORY MODEL - Catalytic Converter Types
# ============================================

class Category(models.Model):
    """Categories for different types of catalytic converters"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


# ============================================
# PRODUCT MODEL (Enhanced for Catalytic Converters)
# ============================================

class Product(models.Model):
    """Individual catalytic converter"""
    
    # Basic Info
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(
        upload_to='products/', 
        null=True, 
        blank=True
    )
    
    # Categorization
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='products'
    )
    
    # Package Association
    package = models.ForeignKey(
        Package,
        on_delete=models.SET_NULL,
        related_name='products',
        null=True,
        blank=True,
        help_text="Package this cat converter belongs to"
    )
    
    # SMASH-Specific Fields
    unique_unit_id = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique identifier for this converter"
    )
    
    FULLNESS_CHOICES = [
        ('FULL', 'Full (1.0x)'),
        ('THREE_QUARTER', '3/4 (0.75x)'),
        ('HALF', '1/2 (0.5x)'),
        ('ONE_QUARTER', '1/4 (0.25x)'),
        ('EMPTY', 'Empty (0x)')
    ]
    fullness = models.CharField(
        max_length=20,
        choices=FULLNESS_CHOICES,
        default='FULL',
        help_text="Honeycomb fullness level"
    )
    
    # Appraisal Info
    appraisal_category = models.CharField(
        max_length=50,
        blank=True,
        help_text="e.g., Exotic, XL Fin, GM Bale, Diesel"
    )
    
    appraisal_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Per-unit appraisal value ($/lb)"
    )
    
    # Bidding
    starting_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Minimum bid amount"
    )
    
    current_item_bid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Current highest bid for this item"
    )
    
    # Ownership
    seller = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='products'
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Catalytic Converter'
        verbose_name_plural = 'Catalytic Converters'
    
    def __str__(self):
        return f"{self.unique_unit_id} - {self.title}"
    
    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'pk': self.pk})
    
    def get_fullness_multiplier(self):
        """Get numeric multiplier for fullness"""
        multipliers = {
            'FULL': 1.0,
            'THREE_QUARTER': 0.75,
            'HALF': 0.5,
            'ONE_QUARTER': 0.25,
            'EMPTY': 0.0
        }
        return multipliers.get(self.fullness, 1.0)


# ============================================
# BID MODEL - Enhanced for Item-by-Item Bidding
# ============================================

class Bid(models.Model):
    """Individual bid on a catalytic converter"""
    
    # Relationships
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='bids'
    )
    
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='bids',
        help_text="The specific cat converter being bid on"
    )
    
    # Optional: Link to package and sale for aggregation
    package = models.ForeignKey(
        Package,
        on_delete=models.CASCADE,
        related_name='bids',
        null=True,
        blank=True
    )
    
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name='bids',
        null=True,
        blank=True
    )
    
    # Bid Details
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Bid amount in dollars"
    )
    
    # Appraisal Details (for item-by-item)
    appraisal_category = models.CharField(
        max_length=50,
        blank=True,
        help_text="Category selected during appraisal"
    )
    
    appraisal_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Base value selected"
    )
    
    fullness_applied = models.CharField(
        max_length=20,
        blank=True,
        help_text="Fullness level applied to this bid"
    )
    
    # Status
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACTIVE', 'Active'),
        ('WINNING', 'Winning'),
        ('OUTBID', 'Outbid'),
        ('WON', 'Won'),
        ('LOST', 'Lost')
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Bid'
        verbose_name_plural = 'Bids'
    
    def __str__(self):
        return f"{self.user.username} - ${self.amount} on {self.product.unique_unit_id}"


# ============================================
# FAVORITE/WATCHLIST MODEL
# ============================================

class Favorite(models.Model):
    """User's favorite/watched sales"""
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='favorites'
    )
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'sale')
        verbose_name = 'Favorite Sale'
        verbose_name_plural = 'Favorite Sales'
    
    def __str__(self):
        return f"{self.user.username} watching {self.sale.lot_number}"


# ============================================
# PRODUCT IMAGE MODEL (for multiple images)
# ============================================

class ProductImage(models.Model):
    """Additional images for a product"""
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='additional_images'
    )
    image = models.ImageField(upload_to='products/additional/')
    caption = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['uploaded_at']
    
    def __str__(self):
        return f"Image for {self.product.unique_unit_id}"


# ============================================
# APPRAISAL CATEGORY PRESET
# ============================================

class AppraisalCategory(models.Model):
    """Predefined appraisal categories with values"""
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    base_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Base value per unit ($/lb)"
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = 'Appraisal Category'
        verbose_name_plural = 'Appraisal Categories'
    
    def __str__(self):
        return f"{self.name} - ${self.base_value}"
