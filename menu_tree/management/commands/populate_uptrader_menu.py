from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from menu_tree.models import (
    MenuItem,
)


class Command(BaseCommand):
    help = "Заполняет базу данных указанной структурой меню."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Удалить все существующие пункты меню перед заполнением.",
        )
        parser.add_argument(
            "--menu_name",
            type=str,
            default="main_menu",
            help="Укажите имя (slug) для создаваемого меню.",
        )

    def _create_menu_item(self, name, menu_name, order, parent=None, base_path=""):
        """Вспомогательная функция для создания пункта меню и логирования."""
        # Генерируем простой explicit_url
        slug = slugify(name)
        if parent and hasattr(parent, "generated_path"):
            item_path = f"{parent.generated_path}{slug}/"
        else:
            item_path = f"/{slug}/" if not base_path else f"{base_path}{slug}/"

        item = MenuItem.objects.create(
            name=name,
            menu_name=menu_name,
            parent=parent,
            order=order,
            explicit_url=item_path,
        )
        item.generated_path = item_path
        self.stdout.write(
            self.style.SUCCESS(f"Создан: '{item.name}' (URL: {item.explicit_url})")
        )
        return item

    @transaction.atomic
    def handle(self, *args, **options):
        menu_name_to_seed = options["menu_name"]

        if options["clear"]:
            self.stdout.write(
                self.style.WARNING(
                    f"Удаление существующих пунктов меню для '{menu_name_to_seed}'..."
                )
            )
            MenuItem.objects.filter(menu_name=menu_name_to_seed).delete()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Все существующие пункты меню для '{menu_name_to_seed}' удалены."
                )
            )
            exit()

        self.stdout.write(
            self.style.HTTP_INFO(f"Начало заполнения меню '{menu_name_to_seed}'...")
        )

        # Уровень 1: Корневые элементы
        products = self._create_menu_item("Products", menu_name_to_seed, 0)
        about = self._create_menu_item("About", menu_name_to_seed, 10)
        services = self._create_menu_item("Services", menu_name_to_seed, 20)

        # Уровень 2: Дети "Products"
        forex_crm = self._create_menu_item(
            "Forex CRM", menu_name_to_seed, 0, parent=products
        )
        self._create_menu_item(
            "White Label Social Trading Platform",
            menu_name_to_seed,
            10,
            parent=products,
        )
        self._create_menu_item(
            "Prop Trading Solutions", menu_name_to_seed, 20, parent=products
        )

        # Уровень 3: Дети "Forex CRM"
        self._create_menu_item("Sales Module", menu_name_to_seed, 0, parent=forex_crm)
        self._create_menu_item("Trader's room", menu_name_to_seed, 10, parent=forex_crm)
        self._create_menu_item(
            "Forex Back Office", menu_name_to_seed, 20, parent=forex_crm
        )

        # Уровень 2: Дети "About"
        self._create_menu_item("Contacts", menu_name_to_seed, 0, parent=about)
        self._create_menu_item("News", menu_name_to_seed, 10, parent=about)
        self._create_menu_item("Article", menu_name_to_seed, 20, parent=about)
        self._create_menu_item("Events", menu_name_to_seed, 30, parent=about)
        self._create_menu_item("Our Partners", menu_name_to_seed, 40, parent=about)
        self._create_menu_item("About Our Company", menu_name_to_seed, 50, parent=about)
        self._create_menu_item("Media", menu_name_to_seed, 60, parent=about)

        # Уровень 2: Дети "Services"
        self._create_menu_item("Legal services", menu_name_to_seed, 0, parent=services)
        self._create_menu_item(
            "Forex Liquidity", menu_name_to_seed, 10, parent=services
        )
        self._create_menu_item(
            "Custom development", menu_name_to_seed, 20, parent=services
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Заполнение меню '{menu_name_to_seed}' успешно завершено!"
            )
        )
