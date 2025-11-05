# SMASH Marketplace - Admin Configuration
# File: auctions/admin.py
# Replace your existing admin.py with this

from django.contrib import admin
from .models import (
    Package, Sale, Category, Product, Bid, 
    Favorite, ProductImage, AppraisalCategory
)

# ============================================
# PACKAGE ADMIN
# ============================================

@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'status', 'item_count', 'current_package_bid', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'item_count', 'total_bids']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'status')
        }),
        ('Details', {
            'fields': ('final_weight', 'current_package_bid', 'notes')
        }),
        ('Statistics', {
            'fields': ('item_count', 'total_bids', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# ============================================
# SALE ADMIN
# ============================================

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['lot_number', 'title', 'seller', 'status', 'unit_count', 
                    'current_sale_bid', 'bid_due_date', 'created_at']
    list_filter = ['status', 'seller_type', 'created_at']
    search_fields = ['lot_number', 'title', 'seller__username', 'zip_code']
    readonly_fields = ['created_at', 'updated_at', 'published_at', 'total_packages', 'total_items']
    filter_horizontal = ['packages', 'watchers']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('lot_number', 'title', 'description', 'seller')
        }),
        ('Sale Details', {
            'fields': ('packages', 'unit_count', 'total_weight', 'seller_type')
        }),
        ('Location & Logistics', {
            'fields': ('zip_code', 'pickup_instructions')
        }),
        ('Bidding', {
            'fields': ('bid_due_date', 'status', 'current_sale_bid', 'winning_bid')
        }),
        ('Watchers', {
            'fields': ('watchers',),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('total_packages', 'total_items', 'created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )


# ============================================
# CATEGORY ADMIN
# ============================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


# ============================================
# PRODUCT ADMIN (Enhanced)
# ============================================

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'caption']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['unique_unit_id', 'title', 'category', 'package', 'fullness', 
                    'appraisal_category', 'current_item_bid', 'seller', 'is_active', 'created_at']
    list_filter = ['category', 'fullness', 'is_active', 'created_at', 'appraisal_category']
    search_fields = ['unique_unit_id', 'title', 'description', 'seller__username']
    readonly_fields = ['created_at', 'updated_at', 'current_item_bid']
    inlines = [ProductImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('unique_unit_id', 'title', 'description', 'image', 'category', 'seller')
        }),
        ('Package Association', {
            'fields': ('package',)
        }),
        ('SMASH Details', {
            'fields': ('fullness', 'appraisal_category', 'appraisal_value')
        }),
        ('Pricing', {
            'fields': ('starting_price', 'current_item_bid')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new product
            if not obj.seller_id:
                obj.seller = request.user
        super().save_model(request, obj, form, change)


# ============================================
# BID ADMIN
# ============================================

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'amount', 'appraisal_category', 'status', 'created_at']
    list_filter = ['status', 'appraisal_category', 'created_at']
    search_fields = ['user__username', 'product__unique_unit_id', 'product__title']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Bid Information', {
            'fields': ('user', 'product', 'amount', 'status')
        }),
        ('Associations', {
            'fields': ('package', 'sale')
        }),
        ('Appraisal Details', {
            'fields': ('appraisal_category', 'appraisal_value', 'fullness_applied')
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )


# ============================================
# FAVORITE ADMIN
# ============================================

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'sale', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'sale__lot_number']


# ============================================
# APPRAISAL CATEGORY ADMIN
# ============================================

@admin.register(AppraisalCategory)
class AppraisalCategoryAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'base_value', 'is_active', 'sort_order']
    list_filter = ['is_active']
    search_fields = ['code', 'name']
    list_editable = ['is_active', 'sort_order']
    ordering = ['sort_order', 'name']
    
    fieldsets = (
        ('Category Information', {
            'fields': ('code', 'name', 'base_value', 'description')
        }),
        ('Display Settings', {
            'fields': ('is_active', 'sort_order')
        }),
    )


# ============================================
# PRODUCT IMAGE ADMIN (if needed separately)
# ============================================

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'caption', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['product__unique_unit_id', 'product__title', 'caption']
