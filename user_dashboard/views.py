from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from auctions.models import *


class UserDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'user_dashboard/user_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['favorites'] = Favorite.objects.filter(user=self.request.user)
        context['products_on_sale'] = Product.objects.filter(seller=self.request.user)
        context['bids_submitted'] = Bid.objects.filter(user=self.request.user)
        return context


class FavoritesView(LoginRequiredMixin, ListView):
    template_name = 'user_dashboard/favorites.html'
    context_object_name = 'favorites'

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)


class ProductsOnSaleView(LoginRequiredMixin, ListView):
    template_name = 'user_dashboard/products_on_sale.html'
    context_object_name = 'products_on_sale'

    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user)


class SubmittedBidsView(LoginRequiredMixin, ListView):
    template_name = 'user_dashboard/submitted_bids.html'
    context_object_name = 'bids_submitted'

    def get_queryset(self):
        return Bid.objects.filter(user=self.request.user)
