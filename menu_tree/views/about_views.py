from .general_views import BasePagePlaceholderView


class AboutDetailPageView(BasePagePlaceholderView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        about_slug = kwargs.get("about_slug", "unknown_service")
        context["page_title"] = f"Услуга: {about_slug.replace('-', ' ').title()}"
        context["page_content"] = f"Подробное описание '{about_slug}'"
        return context
