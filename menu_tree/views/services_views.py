from .general_views import BasePagePlaceholderView


class ServiceDetailPageView(BasePagePlaceholderView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service_slug = kwargs.get("service_slug", "unknown_service")
        context["page_title"] = f"Услуга: {service_slug.replace('-', ' ').title()}"
        context["page_content"] = f"Подробное описание '{service_slug}'"
        return context
