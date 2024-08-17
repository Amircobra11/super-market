from django.db.models import Count
from django.shortcuts import render
from product_module.models import Product, ProductCategory
from utils.convertors import group_list
from django.views import View
from django.views.generic.base import TemplateView
from utils.http_service import get_client_ip
from site_module.models import SiteSettings, FooterLinkBox, Slider, FooterLink
from django.db.models import Sum


class HomeView(TemplateView):
    template_name = 'home_module/index_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sliders = Slider.objects.filter(is_active=True)
        context['sliders'] = sliders
        latest_products = Product.objects.filter(is_active=True, is_delete=False).order_by('-id')[:12]
        most_visited_products = Product.objects.filter(is_active=True, is_delete=False).annotate(visit_count=Count('productvisit')).order_by('-visit_count')[:12]
        context['latest_products'] = group_list(latest_products)
        context['most_visited_products'] = group_list(most_visited_products)
        categories = list(ProductCategory.objects.annotate(product_count=Count('product_categories')).filter(is_active=True, is_delete=False, product_count__gt=0)[:6])
        categories_products = []
        for category in categories:
            item = {
                'id': category.id,
                'title': category.title,
                'products': list(category.product_categories.all()[:4])
            }
            categories_products.append(item)
        context['categories_products'] = categories_products
        most_bought_products = Product.objects.filter(orderdetail__order__is_paid=True).annotate(order_count=Sum(
            'orderdetail__count'
        )).order_by('-order_count')[:12]
        context['most_bought_products'] = group_list(most_bought_products)
        return context


def site_header_component(request):
    setting: SiteSettings = SiteSettings.objects.filter(is_main_setting=True).first()
    context = {
        'site_settings': setting
    }
    return render(request, 'shared/site_header_component.html', context)


def site_footer_component(request):
    setting: SiteSettings = SiteSettings.objects.filter(is_main_setting=True).first()
    footer_link_boxes = FooterLinkBox.objects.all()
    for item in footer_link_boxes:
        footer_links = item.footerlink_set.all()

    context = {
        'site_settings': setting,
        'footer_link_boxes': footer_link_boxes
    }
    return render(request, 'shared/site_footer_component.html', context)


class AboutView(TemplateView):
    template_name = 'home_module/about_page.html'

    def get_context_data(self, **kwargs):
        context = super(AboutView, self).get_context_data(**kwargs)
        site_setting: SiteSettings = SiteSettings.objects.filter(is_main_setting=True).first()
        context['site_setting'] = site_setting
        return context
