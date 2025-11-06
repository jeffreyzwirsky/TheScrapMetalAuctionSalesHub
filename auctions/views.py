# SMASH Marketplace - Views
# Scrap Metal Auction Sales Hub
# File: auctions/views.py
# REPLACE your existing views.py with this complete file

from django.views.generic import ListView, CreateView, UpdateView, DetailView, TemplateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Q
from .models import Product, Sale, Category, Package, Bid, ProductImage
from .forms import ProductForm, BidForm, PackageForm, SaleForm


# ============================================
# PRODUCT (CATALYTIC CONVERTER) VIEWS
# ============================================

class ProductListView(ListView):
    """List all catalytic converters with filters"""
    model = Product
    template_name = 'auctions/product_list.html'
    context_object_name = 'products'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        
        # Filter by category
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__name__iexact=category)
        
        # Filter by package
        package_id = self.request.GET.get('package')
        if package_id:
            queryset = queryset.filter(package__id=package_id)
        
        # Filter by price range
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(current_item_bid__gte=float(min_price))
        if max_price:
            queryset = queryset.filter(current_item_bid__lte=float(max_price))
        
        # Sort
        sort = self.request.GET.get('sort')
        if sort == 'price_asc':
            queryset = queryset.order_by('current_item_bid')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-current_item_bid')
        elif sort == 'unit_id':
            queryset = queryset.order_by('unique_unit_id')
        else:
            queryset = queryset.order_by('-created_at')
        
        # Search
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(description__icontains=search_query) |
                Q(unique_unit_id__icontains=search_query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['packages'] = Package.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        return context


class ProductDetailView(DetailView):
    """Detail view for a single catalytic converter"""
    model = Product
    template_name = 'auctions/product_detail.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        # Get all bids on this product
        context['bids'] = product.bids.all().order_by('-amount')
        context['bid_count'] = product.bids.count()
        
        return context


class CategorySelectView(LoginRequiredMixin, TemplateView):
    """Select category before creating a product"""
    template_name = 'auctions/category_select.html'
    login_url = '/admin/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class ProductCreateView(LoginRequiredMixin, CreateView):
    """Create a new catalytic converter"""
    form_class = ProductForm
    template_name = 'auctions/product_form.html'
    success_url = reverse_lazy('product_list')
    login_url = '/admin/login/'
    
    def get_initial(self):
        initial = super().get_initial()
        category_name = self.request.GET.get('category')
        if category_name:
            try:
                category = Category.objects.get(name=category_name)
                initial['category'] = category.id
            except Category.DoesNotExist:
                pass
        return initial
    
    def form_valid(self, form):
        form.instance.seller = self.request.user
        product = form.save()
        
        # Handle image upload
        image = self.request.FILES.get('image')
        if image:
            ProductImage.objects.create(product=product, image=image)
        
        messages.success(self.request, f"Catalytic converter {product.unique_unit_id} created successfully!")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_update'] = False
        context['page_title'] = 'Add New Catalytic Converter'
        return context


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing catalytic converter"""
    model = Product
    form_class = ProductForm
    template_name = 'auctions/product_form.html'
    success_url = reverse_lazy('product_list')
    
    def dispatch(self, request, *args, **kwargs):
        product = self.get_object()
        
        # Only seller can update, and only if no bids exist
        if product.seller != request.user:
            raise PermissionDenied("You are not allowed to update this product")
        
        if product.bids.exists():
            messages.error(request, "Cannot update product with existing bids")
            return redirect('product_detail', pk=product.pk)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_update'] = True
        context['product'] = self.get_object()
        context['page_title'] = f'Edit {self.get_object().unique_unit_id}'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, "Catalytic converter updated successfully!")
        return super().form_valid(form)


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a catalytic converter"""
    model = Product
    success_url = reverse_lazy('product_list')
    template_name = 'auctions/product_delete.html'
    
    def get_object(self):
        product = super().get_object()
        
        # Only seller can delete, and only if no bids
        if self.request.user != product.seller:
            raise PermissionDenied("You are not allowed to delete this product")
        
        if product.bids.exists():
            raise PermissionDenied("Cannot delete product with existing bids")
        
        return product
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, "Catalytic converter deleted successfully!")
        return super().delete(request, *args, **kwargs)


# ============================================
# BIDDING VIEWS
# ============================================

def place_bid(request, pk):
    """Place a bid on a catalytic converter"""
    product = get_object_or_404(Product, pk=pk)
    
    # Check authentication
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to place bids.")
        return redirect('login')
    
    # Prevent bidding on own product
    if request.user == product.seller:
        messages.error(request, "You cannot bid on your own product.")
        return redirect('product_detail', pk=product.pk)
    
    if request.method == 'POST':
        bid_amount = request.POST.get('bid_amount')
        
        try:
            # Create bid
            bid = Bid(
                product=product,
                user=request.user,
                amount=bid_amount,
                package=product.package,
                appraisal_category=request.POST.get('appraisal_category', ''),
                appraisal_value=request.POST.get('appraisal_value', None),
                fullness_applied=request.POST.get('fullness_applied', '')
            )
            bid.full_clean()
            bid.save()
            
            # Update product current bid
            product.current_item_bid = bid.amount
            product.save()
            
            messages.success(request, f"Your bid of ${bid_amount} has been placed successfully!")
            return redirect('product_detail', pk=product.pk)
            
        except ValidationError as e:
            error_message = str(e)
            messages.error(request, error_message)
            return redirect('product_detail', pk=product.pk)
    
    return redirect('product_detail', pk=product.pk)


# ============================================
# SALE/LOT VIEWS
# ============================================

class SaleListView(ListView):
    """List all active sales (LOTs)"""
    model = Sale
    template_name = 'auctions/sale_list.html'
    context_object_name = 'sales'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Sale.objects.filter(status='ACTIVE')
        
        # Filter by location
        zip_code = self.request.GET.get('zip_code')
        if zip_code:
            queryset = queryset.filter(zip_code__icontains=zip_code)
        
        # Filter by seller type
        seller_type = self.request.GET.get('seller_type')
        if seller_type:
            queryset = queryset.filter(seller_type=seller_type)
        
        # Sort
        sort = self.request.GET.get('sort')
        if sort == 'due_date':
            queryset = queryset.order_by('bid_due_date')
        elif sort == 'unit_count':
            queryset = queryset.order_by('-unit_count')
        else:
            queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['seller_types'] = Sale.SELLER_TYPE_CHOICES
        return context


class SaleDetailView(DetailView):
    """Detail view for a single sale (LOT)"""
    model = Sale
    template_name = 'auctions/sale_detail.html'
    context_object_name = 'sale'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sale = self.get_object()
        
        # Get all products in this sale
        context['products'] = Product.objects.filter(package__in=sale.packages.all())
        
        return context
