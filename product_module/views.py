from django.db.models.aggregates import Count
from django.shortcuts import render, get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic import ListView, DetailView, View
from site_module.models import SiteBanner
from .models import Product, ProductCategory, ProductBrand, ProductVisit, ProductGallery
from django.http import HttpResponseRedirect, HttpRequest
from utils.http_service import get_client_ip
from utils.convertors import group_list


class ProductListView(ListView):
    template_name = 'product_module/product_list.html'
    model = Product
    context_object_name = 'products'
    paginate_by = 9

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ProductListView, self).get_context_data()
        query = Product.objects.all()
        product: Product = query.order_by('-price').first()
        db_max_price = product.price if product is not None else 0
        context['db_max_price'] = db_max_price
        context['start_price'] = self.request.GET.get('start_price') or 0
        context['end_price'] = self.request.GET.get('end_price') or db_max_price
        context['banners'] = SiteBanner.objects.filter(is_active=True,
                                                       position__exact=SiteBanner.SiteBannerPosition.product_list)
        return context

    def get_queryset(self):
        query = super(ProductListView, self).get_queryset()
        category_name = self.kwargs.get('cat')
        brand_name = self.kwargs.get('brand')
        request: HttpRequest = self.request
        start_price = request.GET.get('start_price')
        end_price = request.GET.get('end_price')

        if start_price is not None:
            query = query.filter(price__gte=start_price)

        if end_price is not None:
            query = query.filter(price__lte=end_price)

        if brand_name is not None:
            query = query.filter(brand__url_title__iexact=brand_name)

        if category_name is not None:
            query = query.filter(category__url_title__iexact=category_name)

        return query


class ProductDetailView(DetailView):
    template_name = 'product_module/product_detail.html'
    model = Product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        loaded_product = self.object
        request = self.request
        favorite_product_id = request.session.get('favorite_product_id')
        context['favorite_product_id'] = favorite_product_id == str(loaded_product.id)
        context['banners'] = SiteBanner.objects.filter(is_active=True,
                                                       position__exact=SiteBanner.SiteBannerPosition.product_detail)
        galleries = list(ProductGallery.objects.filter(product_id=loaded_product.id).all())
        galleries.insert(0, loaded_product)
        context['product_galleries_group'] = group_list(galleries, 3)
        context['related_product'] = group_list(
            list(Product.objects.filter(brand_id=loaded_product.brand_id).exclude(pk=loaded_product.id).all()[:12]), 3)
        user_id = None
        if self.request.user.is_authenticated:
            user_id = self.request.user.id
        user_ip = get_client_ip(self.request)
        has_been_visited = ProductVisit.objects.filter(ip__iexact=user_ip, product_id=loaded_product.id).exists()
        if not has_been_visited:
            new_visit = ProductVisit(ip=user_ip, user_id=user_id, product_id=loaded_product.id)
            new_visit.save()
        return context


class AddProductFavorite(View):
    def post(self, request):
        product_id = request.POST['product_id']
        product = Product.objects.get(pk=product_id)
        request.session['product_favorite'] = product_id
        return HttpResponseRedirect(product.get_absolute_url())


def product_categories_component(request: HttpRequest):
    product_categories = ProductCategory.objects.filter(is_active=True, is_delete=False)
    context = {
        'categories': product_categories
    }
    return render(request, 'product_module/components/product_categories_component.html', context)


def product_brands_component(request: HttpRequest):
    product_brands = ProductBrand.objects.annotate(product_counts=Count('product')).filter(is_active=True)
    context = {
        'brands': product_brands
    }
    return render(request, 'product_module/components/product_brands_component.html', context)



