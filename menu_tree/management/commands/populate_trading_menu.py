from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from menu_tree.models import MenuItem


class Command(BaseCommand):
    help = "Заполняет базу данных пунктами для трейдинг-меню (secondary_menu)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help='Удалить все существующие пункты для "secondary_menu" перед заполнением.',
        )
        parser.add_argument(
            "--menu_name",
            type=str,
            default="secondary_menu",
            help="Имя (slug) для создаваемого трейдинг-меню (по умолчанию: secondary_menu).",
        )

    def _create_menu_item(
        self,
        name,
        menu_name_slug,
        order,
        parent=None,
        base_path_prefix="",
        explicit_url_override=None,
    ):
        item_path = ""
        if explicit_url_override:
            item_path = explicit_url_override
        else:
            slug = slugify(name)
            current_level_path = f"{slug}/"
            if parent and hasattr(parent, "generated_path"):
                item_path = f"{parent.generated_path}{current_level_path}"
            else:
                item_path = (
                    f"/{base_path_prefix.strip('/')}/{current_level_path}".replace(
                        "//", "/"
                    )
                )

        item, created = MenuItem.objects.get_or_create(
            name=name,
            menu_name=menu_name_slug,
            parent=parent,
            defaults={"order": order, "explicit_url": item_path},
        )

        item.generated_path = item_path

        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Создан: '{item.name}' (Меню: {menu_name_slug}, URL: {item.explicit_url})"
                )
            )
        else:
            updated_fields = []
            if item.order != order:
                item.order = order
                updated_fields.append("order")
            if item.explicit_url != item_path:
                item.explicit_url = item_path
                updated_fields.append("explicit_url")

            if updated_fields:
                item.save(update_fields=updated_fields)
                self.stdout.write(
                    self.style.NOTICE(
                        f"Обновлен: '{item.name}' (Меню: {menu_name_slug}, URL: {item.explicit_url}) - поля: {', '.join(updated_fields)}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.NOTICE(
                        f"Пункт '{item.name}' (Меню: {menu_name_slug}) уже существует и не требует обновления."
                    )
                )
        return item

    @transaction.atomic
    def handle(self, *args, **options):
        menu_to_seed = options["menu_name"]

        if options["clear"]:
            self.stdout.write(
                self.style.WARNING(
                    f"Удаление существующих пунктов меню для '{menu_to_seed}'..."
                )
            )
            MenuItem.objects.filter(menu_name=menu_to_seed).delete()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Все существующие пункты меню для '{menu_to_seed}' удалены."
                )
            )

        self.stdout.write(
            self.style.HTTP_INFO(
                f"--- Начало заполнения меню '{menu_to_seed}' (Трейдинг) ---"
            )
        )

        trading_base_path = "trading"

        market_analysis = self._create_menu_item(
            "Market Analysis", menu_to_seed, 0, base_path_prefix=trading_base_path
        )
        trading_tools = self._create_menu_item(
            "Trading Tools", menu_to_seed, 10, base_path_prefix=trading_base_path
        )
        education = self._create_menu_item(
            "Education", menu_to_seed, 20, base_path_prefix=trading_base_path
        )
        account = self._create_menu_item(
            "My Account", menu_to_seed, 30, base_path_prefix=trading_base_path
        )

        self._create_menu_item(
            "Economic Calendar", menu_to_seed, 0, parent=market_analysis
        )
        self._create_menu_item(
            "Technical Charts", menu_to_seed, 10, parent=market_analysis
        )
        self._create_menu_item(
            "News & Sentiments", menu_to_seed, 20, parent=market_analysis
        )
        self._create_menu_item(
            "Analyst Reviews", menu_to_seed, 30, parent=market_analysis
        )

        calculators_parent_obj = self._create_menu_item(
            "Calculators", menu_to_seed, 0, parent=trading_tools
        )
        self._create_menu_item(
            "Platform Downloads", menu_to_seed, 10, parent=trading_tools
        )
        self._create_menu_item("VPS Hosting", menu_to_seed, 20, parent=trading_tools)

        self._create_menu_item(
            "Pip Calculator", menu_to_seed, 0, parent=calculators_parent_obj
        )
        self._create_menu_item(
            "Margin Calculator", menu_to_seed, 10, parent=calculators_parent_obj
        )
        self._create_menu_item(
            "Profit Calculator", menu_to_seed, 20, parent=calculators_parent_obj
        )

        self._create_menu_item("Trading Basics", menu_to_seed, 0, parent=education)
        self._create_menu_item(
            "Advanced Strategies", menu_to_seed, 10, parent=education
        )
        self._create_menu_item("Webinars", menu_to_seed, 20, parent=education)
        self._create_menu_item("Glossary", menu_to_seed, 30, parent=education)

        self._create_menu_item(
            "Dashboard",
            menu_to_seed,
            0,
            parent=account,
            explicit_url_override="/user/dashboard/",
        )
        self._create_menu_item(
            "Deposits & Withdrawals",
            menu_to_seed,
            10,
            parent=account,
            explicit_url_override="/user/funding/",
        )
        self._create_menu_item(
            "Trading History",
            menu_to_seed,
            20,
            parent=account,
            explicit_url_override="/user/history/",
        )
        self._create_menu_item(
            "Profile Settings",
            menu_to_seed,
            30,
            parent=account,
            explicit_url_override="/user/settings/",
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"--- Завершено заполнение меню '{menu_to_seed}' (Трейдинг) ---"
            )
        )
