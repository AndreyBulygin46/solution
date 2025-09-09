from django.contrib import admin
from .models import Quote, ViewCounter, Vote
from django.utils.html import format_html


class ViewCounterInline(admin.TabularInline):
    model = ViewCounter
    extra = 0  # Не показывать пустую форму
    can_delete = False  # Запретить удаление
    readonly_fields = ('count',)  # Только для чтения


class VoteInline(admin.TabularInline):
    model = Vote
    extra = 0
    can_delete = False
    readonly_fields = ('user', 'is_like')  # Показать пользователя и тип голоса


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'source',
        'author',
        'weight',
        'created_at',
        'views_count',
    )
    search_fields = ('text', 'source', 'author__username')
    list_filter = ('source', 'created_at', 'author')
    readonly_fields = ('created_at',)
    # Отображение статистики внутри цитаты
    inlines = [ViewCounterInline, VoteInline]

    def views_count(self, obj):
        """Количество просмотров цитаты."""
        return obj.viewcounter.count if hasattr(obj, 'viewcounter') else 0
    views_count.short_description = 'Просмотры'


admin.site.register(ViewCounter)
admin.site.register(Vote)
