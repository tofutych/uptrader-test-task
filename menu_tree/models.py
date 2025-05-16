from django.db import models
from django.urls import NoReverseMatch, reverse


class MenuItem(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Название пункта",
    )
    menu_name = models.CharField(
        max_length=100,
        verbose_name="Название меню",
        db_index=True,
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.CASCADE,
        verbose_name="Родительский пункт",
    )
    explicit_url = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Явный URL",
        help_text="Например, /about/. Используется, если Named URL не указан.",
    )
    named_url = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Named URL",
        help_text="Например, 'article_list'. Приоритетнее Явного URL.",
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок",
        help_text=("Для сортировки пунктов на одном уровне."),
    )

    class Meta:
        verbose_name = "Пункт меню"
        verbose_name_plural = "Пункты меню"
        ordering = [
            "parent__id",
            "order",
            "name",
        ]

    def get_url(self):
        if self.named_url:
            try:
                return reverse(self.named_url)
            except NoReverseMatch:
                return self.explicit_url or "#"
        return self.explicit_url or "#"

    def get_indent(self):
        level = 0
        p = self.parent
        while p:
            level += 1
            p = p.parent
        return level

    def __str__(self):
        path = [self.name]
        p = self.parent
        while p:
            path.insert(0, p.name)
            p = p.parent
        return f"{self.menu_name} :: {' -> '.join(path)}"
