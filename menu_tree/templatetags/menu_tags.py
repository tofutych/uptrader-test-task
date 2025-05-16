from django import template

from menu_tree.services import build_menu_tree

register = template.Library()


@register.inclusion_tag(
    "menu_tree/partials/menu/menu_template.html", takes_context=True
)
def draw_menu(context, menu_name):
    request = context.get("request")
    current_path = request.path if request else ""

    processed_root_items = build_menu_tree(menu_name, current_path, request)

    return {
        "menu_items": processed_root_items,
        "menu_name": menu_name,
    }
