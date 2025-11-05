from django.views.generic import ListView, CreateView, UpdateView, DetailView, TemplateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from .models import *
from .forms import *
from django.shortcuts import render


class ProductListView(ListView):
    model = Product
    template_name = 'auctions/product_list.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        queryset = Product.objects.all()

        # Filter by category
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__name__iexact=category)

        # Filter by price range
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(current_bid__gte=float(min_price))
        if max_price:
            queryset = queryset.filter(current_bid__lte=float(max_price))

        # Sort by current bid
        sort = self.request.GET.get('sort')
        if sort == 'price_asc':
            queryset = queryset.order_by('current_bid')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-current_bid')
        else:
            queryset = queryset.order_by('-created_at')

        # Search by title or description
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | Q(description__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        return context

    def get_paginate_by(self, queryset):
        return self.paginate_by


class ProductDetailView(DetailView):
    template_name = 'auctions/product_detail.html'
    context_object_name = 'product'


    def get_object(self):
        pk = self.kwargs.get('pk')
        return get_object_or_404(Product.objects.select_subclasses(), pk=pk)  # This is for accessing subclasses' attributes

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        if self.request.user.is_authenticated:
            context['is_favorited'] = Favorite.objects.filter(user=self.request.user, product=product).exists()
        return context


class CategorySelectView(LoginRequiredMixin, TemplateView):
    template_name = 'auctions/category_select.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()  # Fetch categories from the database
        return context


class ProductCreateView(CreateView):
    template_name = 'auctions/product_form.html'
    success_url = reverse_lazy('product_list')


    def get_form_class(self):
        category = self.request.GET.get('category')
        particular_form = form_mapping.get(category, ProductForm)  # Use a mapping to select the right form
        return particular_form

    def get_initial(self):
        initial = super().get_initial()
        category_name = self.request.GET.get('category')
        category = Category.objects.get(name=category_name)
        initial['category'] = category.id
        return initial

    def form_valid(self, form):
        form.instance.seller = self.request.user
        product = form.save()  # Save the product first

        # Handle optional image uploads
        image = self.request.FILES.get('image')  # Get the uploaded images
        if image:  # Only save images if any were uploaded
            ProductImage.objects.create(product=product, image=image)
        return super().form_valid(form)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_update'] = False  # This is a creation view
        return context


class ProductUpdateView(UpdateView):
    template_name = 'auctions/product_form.html'
    success_url = reverse_lazy('product_list')

    def get_object(self):
        pk = self.kwargs.get('pk')
        return get_object_or_404(Product.objects.select_subclasses(), pk=pk)

    def get_form_class(self):
        category = self.get_object().category.name
        particular_form = form_mapping.get(category, ProductForm)  # Use a mapping to select the right form
        return particular_form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_update'] = True  # This is an update view
        context['product'] = self.get_object()
        return context

    def dispatch(self, request, *args, **kwargs):
        product = self.get_object()
        if product.seller != request.user or product.bids.exists():
            raise PermissionDenied("You are not allowed to update this product")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        product = form.save(commit=False)

        # Delete image
        delete_image_id = self.request.POST.get('delete_image')
        if delete_image_id:
            image_to_delete = get_object_or_404(ProductImage, id=delete_image_id)
            image_to_delete.delete()
            messages.success(self.request, "Image deleted successfully.")
            return self.render_to_response(self.get_context_data(form=form))

        # Upload image
        image = form.cleaned_data.get('image')  # Use get to avoid KeyError
        if image:
            if product.images.exists():  # Check if an image already exists
                messages.error(self.request, "You can't add images when one already exists.")
                return self.form_invalid(form)
            ProductImage.objects.create(product=product, image=image)


        # Check if any bids exist for the product
        if product.bids.exists():
            messages.error(self.request, "You cannot update this product because there are existing bids.")
            return self.form_invalid(form)

        # Save the product if no bids exist
        product.save()
        return super().form_valid(form)


class ProductDeleteView(DeleteView):
    success_url = reverse_lazy('product_list')
    template_name = 'auctions/product_delete.html'

    def get_object(self):
        pk = self.kwargs.get('pk')
        product = get_object_or_404(Product, pk=pk)
        if self.request.user != product.seller or product.bids.exists():
            raise PermissionDenied
        return product

    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)



# Add/Remove Favorites



def toggle_favorite(request, pk):
    product = get_object_or_404(Product, pk=pk)

    # Ensure the user is authenticated
    if not request.user.is_authenticated:
        messages.error(request, "You must login to add favorites.")
        return redirect('product_detail', pk=product.pk)

    # Prevent users from adding their own products as favorites
    if product.seller == request.user:
        messages.error(request, "You can't add your own product to favorites.")
        return redirect('product_detail', pk=product.pk)

    # Toggle favorite status
    favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)
    if created:
        messages.success(request, "Added to favorites.")
    else:
        favorite.delete()  # Remove from favorites
        messages.success(request, "Removed from favorites.")

    return redirect('product_detail', pk=product.pk)


# Bidding

def place_bid(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.user == product.seller:
        messages.error(request, "You cannot bid on your own product.")
        return redirect('product_detail', pk=product.pk)

    if request.method == 'POST':
        bid_amount = request.POST.get('bid_amount')



        # Validate and create the bid
        try:
            bid = Bid(product=product, user=request.user, amount=bid_amount)
            bid.full_clean()  # This will call the clean method
            bid.save()

            # Update the current bid on the product
            product.current_bid = bid.amount
            product.save()
            messages.success(request, "Your bid has been placed successfully!")
            return redirect('product_detail', pk=product.pk)

        except ValidationError as e:
            error_message = e.message_dict.get('amount', "Invalid bid")
            messages.error(request, error_message)

    return render(request, 'auctions/product_detail.html', {'product': product})
