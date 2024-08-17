from .forms import ContactUsModelForm
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from .models import ContactUs, UserProfile
from site_module.models import SiteSettings


class ContactUsView(CreateView):
    model = ContactUs
    form_class = ContactUsModelForm
    template_name = 'contact_module/contact_us_page.html'
    success_url = '/contact-us/'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        setting: SiteSettings = SiteSettings.objects.filter(is_main_setting=True).first()
        context['site_setting'] = setting
        return context


def store_file(file):
    with open('temp/image.jpg', 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)


class CreateProfileView(CreateView):
    template_name = 'contact_module/create_profile_page.html'
    model = UserProfile
    fields = '__all__'
    success_url = '/contact-us/create-profile/'


class ProfilesView(ListView):
    template_name = 'contact_module/profiles_list_page.html'
    model = UserProfile
    fields = "__all__"
    context_object_name = 'profiles'
