import logging

from django.urls import (
    Resolver404,
    resolve,
)

from menu_tree.models import MenuItem

logger = logging.getLogger(__name__)


def _get_url_specificity(item_url, current_path, item, is_named_url_match=False):
    specificity = 0
    if not item_url or item_url == "#":
        return 0

    try:
        if item_url == current_path:
            specificity = len(item_url) * 100
        elif is_named_url_match:
            specificity = len(item_url) * 50
        elif current_path.startswith(item_url):
            if item_url != "/" or item_url == current_path:
                if len(current_path) == len(item_url) or (
                    len(current_path) > len(item_url)
                    and current_path[len(item_url)] == "/"
                ):
                    specificity = len(item_url)
    except TypeError as e:
        logger.error(
            f"TypeError в _get_url_specificity для item ID {item.id if item else 'Unknown'}: {e}. item_url='{item_url}', current_path='{current_path}'"
        )
        return 0
    return specificity


def _initialize_menu_items_attributes(all_items_list):
    logger.debug(f"Инициализация атрибутов для {len(all_items_list)} пунктов меню...")
    for item in all_items_list:
        item.children_list = []
        item.is_active = False
        item.is_expanded = False
        item.level = 0
        try:
            item.actual_url = item.get_url()
            if item.actual_url == "#" or not item.actual_url:
                logger.debug(
                    f"Пункт меню '{item.name}' (ID: {item.id}) имеет URL-заглушку или пустой URL: '{item.actual_url}'"
                )
        except Exception as e:
            logger.error(
                f"Ошибка при вызове get_url() для пункта '{item.name}' (ID: {item.id}): {e}. Установлен URL по умолчанию '#'."
            )
            item.actual_url = "#"
    logger.debug("Инициализация атрибутов завершена.")


def _assign_item_levels_recursive(item_list, current_level=0):
    for i in item_list:
        i.level = current_level
        if hasattr(i, "children_list") and i.children_list:
            _assign_item_levels_recursive(i.children_list, current_level + 1)


def _determine_active_item(
    all_items_list, current_path, current_resolver_match, menu_name_for_logs
):
    active_item_obj = None
    highest_specificity = -1
    logger.debug(f"Определение активного пункта для меню '{menu_name_for_logs}'...")

    for item in all_items_list:
        is_current_path_matching_item_named_url = False
        if item.named_url and current_resolver_match:
            if hasattr(current_resolver_match, "namespace") and hasattr(
                current_resolver_match, "url_name"
            ):
                resolved_full_name = (
                    f"{current_resolver_match.namespace}:{current_resolver_match.url_name}"
                    if current_resolver_match.namespace
                    else current_resolver_match.url_name
                )
                if item.named_url == resolved_full_name:
                    is_current_path_matching_item_named_url = True
                elif (
                    not current_resolver_match.namespace
                    and item.named_url == current_resolver_match.url_name
                ):
                    is_current_path_matching_item_named_url = True
            else:
                logger.warning(
                    f"current_resolver_match (для {current_path}) не имеет атрибутов namespace/url_name: {current_resolver_match}"
                )

        specificity = _get_url_specificity(
            item.actual_url,
            current_path,
            item,
            is_current_path_matching_item_named_url,
        )

        if specificity > highest_specificity:
            highest_specificity = specificity
            active_item_obj = item

    return active_item_obj, highest_specificity


def _build_tree_hierarchy(all_items_list, items_dict, menu_name_for_logs):
    root_items = []
    logger.debug(f"Построение иерархии для меню '{menu_name_for_logs}'...")

    for item in all_items_list:
        if item.parent_id:
            parent_item = items_dict.get(item.parent_id)
            if parent_item:
                parent_item.children_list.append(item)
            else:
                logger.warning(
                    f"Пункт '{item.name}' (ID:{item.id}) имеет parent_id={item.parent_id}, "
                    f"но родитель не найден в items_dict для меню '{menu_name_for_logs}'. "
                    f"Он не будет включен в children_list."
                )
        elif not item.parent_id:
            root_items.append(item)

    try:
        for item in all_items_list:
            if hasattr(item, "children_list"):
                item.children_list.sort(key=lambda x: (x.order, x.name))
        logger.debug(f"Сортировка '{menu_name_for_logs}' завершена.")
    except AttributeError as e:
        logger.error(f"Ошибка атрибута при сортировке '{menu_name_for_logs}': {e}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка при сортировке '{menu_name_for_logs}': {e}")

    logger.debug(
        f"Иерархия для меню '{menu_name_for_logs}' построена. {len(root_items)} корневых элементов."
    )
    return root_items


def _set_expanded_flags_for_active_branch(
    all_items_list, active_item_obj, items_dict, menu_name_for_logs
):
    if not active_item_obj:
        logger.debug(
            f"Нет активного элемента для меню '{menu_name_for_logs}', флаги is_expanded не устанавливаются."
        )
        return

    ancestor_ids_of_active = _get_ancestor_ids_for_active(
        active_item_obj, items_dict, menu_name_for_logs
    )

    logger.debug(
        f"Установка флагов is_expanded для активной ветки меню '{menu_name_for_logs}'..."
    )
    for item in all_items_list:
        if item.id in ancestor_ids_of_active:
            item.is_expanded = True
    logger.debug(f"Флаги is_expanded для меню '{menu_name_for_logs}' установлены.")


def _get_ancestor_ids_for_active(active_item_obj, items_dict, menu_name_for_logs):
    if not active_item_obj:
        return set()

    ancestor_ids = set()
    logger.debug(
        f"Сбор предков для активного пункта '{active_item_obj.name}' в меню '{menu_name_for_logs}'..."
    )
    curr = active_item_obj
    while curr:
        ancestor_ids.add(curr.id)
        if curr.parent_id and curr.parent_id not in items_dict:
            logger.warning(
                f"Пункт '{curr.name}' (ID: {curr.id}) в меню '{menu_name_for_logs}' имеет parent_id={curr.parent_id}, "
                f"но родитель не найден в текущем наборе items_dict."
            )
        curr = items_dict.get(curr.parent_id) if curr.parent_id else None
    logger.debug(
        f"Найденные предки (включая активный) для меню '{menu_name_for_logs}': {ancestor_ids}"
    )
    return ancestor_ids


def build_menu_tree(menu_name_from_tag, current_path, request):
    logger.debug(
        f"--- Начало сборки дерева меню '{menu_name_from_tag}' для пути '{current_path}' ---"
    )
    current_resolver_match = None
    if request:
        try:
            current_resolver_match = resolve(current_path)
            logger.debug(
                f"Путь '{current_path}' разрешен в: name='{current_resolver_match.url_name}', ns='{current_resolver_match.namespace}'"
            )
        except Resolver404:
            logger.warning(f"Путь '{current_path}' не найден (Resolver404).")
        except Exception as e:
            logger.error(f"Ошибка при вызове resolve для пути '{current_path}': {e}")
    else:
        logger.warning("'request' не передан в build_menu_tree.")

    try:
        menu_items_qs = MenuItem.objects.filter(
            menu_name=menu_name_from_tag
        ).select_related("parent")
        all_items_list = list(menu_items_qs)
        if not all_items_list:
            logger.info(f"Для меню '{menu_name_from_tag}' не найдено пунктов.")
            return []
        logger.debug(
            f"Найдено {len(all_items_list)} пунктов для меню '{menu_name_from_tag}'."
        )
    except Exception as e:
        logger.error(f"Ошибка при запросе пунктов меню '{menu_name_from_tag}': {e}")
        return []

    items_dict = {item.id: item for item in all_items_list}

    _initialize_menu_items_attributes(all_items_list)

    active_item_obj, highest_specificity = _determine_active_item(
        all_items_list,
        current_path,
        current_resolver_match,
        menu_name_from_tag,
    )

    if active_item_obj:
        if highest_specificity > 0:
            active_item_obj.is_active = True
            logger.info(
                f"Активный пункт для '{menu_name_from_tag}': '{active_item_obj.name}' (ID:{active_item_obj.id})."
            )
        else:
            logger.info(
                f"Кандидат '{active_item_obj.name}' для '{menu_name_from_tag}' имел специфичность 0. Активный не установлен."
            )
            active_item_obj = None
    else:
        logger.info(f"Активный пункт для '{menu_name_from_tag}' не найден.")

    root_items = _build_tree_hierarchy(all_items_list, items_dict, menu_name_from_tag)

    _set_expanded_flags_for_active_branch(
        all_items_list, active_item_obj, items_dict, menu_name_from_tag
    )

    _assign_item_levels_recursive(root_items)
    logger.debug(f"Уровни вложенности для меню '{menu_name_from_tag}' присвоены.")

    logger.info(
        f"--- Сборка дерева меню '{menu_name_from_tag}' завершена. {len(root_items)} корневых элементов. ---"
    )
    return root_items
