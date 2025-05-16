from .general_views import BasePagePlaceholderView


class ProductsPageView(BasePagePlaceholderView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Products"
        context["page_content"] = "Подробное описание Products"
        return context


class WhiteLabelPageView(BasePagePlaceholderView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "White Label"
        context["page_content"] = "Подробное описание White Label"
        return context


class PropTradingPageView(BasePagePlaceholderView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Prop Trading"
        context["page_content"] = "Подробное описание Prop Trading"
        return context
