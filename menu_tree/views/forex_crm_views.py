from .general_views import BasePagePlaceholderView


class ForexCrmPageView(BasePagePlaceholderView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Forex CRM"
        context["page_content"] = "Подробное описание Forex CRM"
        return context


class ForexCrmDetailPageView(BasePagePlaceholderView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        solution_slug = kwargs.get("crm_solution_slug", "unknown_solution")
        context["page_title"] = f"Услуга: {solution_slug.replace('-', ' ').title()}"
        context["page_content"] = f"Подробное описание '{solution_slug}'"
        return context
