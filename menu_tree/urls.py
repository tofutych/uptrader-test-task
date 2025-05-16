from django.urls import path

from menu_tree.views import (
    about_views,
    forex_crm_views,
    general_views,
    products_views,
    services_views,
)

app_name = "menu_tree"

urlpatterns = [
    path(
        "",
        general_views.HomePageView.as_view(),
        name="home",
    ),
    path(
        "products/",
        general_views.ProductsPageView.as_view(),
        name="products_list",
    ),
    path(
        "products/forex-crm/",
        forex_crm_views.ForexCrmPageView.as_view(),
        name="forex_crm_list",
    ),
    path(
        "products/white-label-social-trading-platform/",
        products_views.WhiteLabelPageView.as_view(),
        name="white_label_detail",
    ),
    path(
        "products/prop-trading-solutions/",
        products_views.PropTradingPageView.as_view(),
        name="prop_trading_detail",
    ),
    path(
        "products/forex-crm/<slug:crm_solution_slug>/",
        forex_crm_views.ForexCrmDetailPageView.as_view(),
        name="solution_detail",
    ),
    path(
        "about/",
        general_views.AboutPageView.as_view(),
        name="about_list",
    ),
    path(
        "about/<slug:about_slug>/",
        about_views.AboutDetailPageView.as_view(),
        name="about_detail",
    ),
    path(
        "services/",
        general_views.ServicesPageView.as_view(),
        name="services_list",
    ),
    path(
        "services/<slug:service_slug>/",
        services_views.ServiceDetailPageView.as_view(),
        name="service_detail",
    ),
]
