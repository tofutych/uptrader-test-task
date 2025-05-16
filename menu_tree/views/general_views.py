from django.views.generic import TemplateView


class BasePagePlaceholderView(TemplateView):
    template_name = "menu_tree/layouts/page_placeholder.html"


class HomePageView(BasePagePlaceholderView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Домашняя страница"
        context["page_content"] = "Подробное описание Home"
        return context


class ProductsPageView(BasePagePlaceholderView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Products"
        context["page_content"] = "Подробное описание Products"
        return context


class AboutPageView(BasePagePlaceholderView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "About"
        context["page_content"] = "Подробное описание About"
        return context


class ServicesPageView(BasePagePlaceholderView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Services"
        context["page_content"] = "Подробное описание Services"
        return context
