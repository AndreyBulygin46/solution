from django.db import models
from django.db.models import F, Func, Value
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Quote(models.Model):
    source = models.CharField(max_length=100)
    text = models.TextField()
    weight = models.PositiveIntegerField(default=1, verbose_name='Вес')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['text'],
                name='unique_text',
                violation_error_message="Цитата уже существует для этого источника"
            ),
            models.CheckConstraint(
                check=~models.Q(source=''),
                name='non_empty_source',
                violation_error_message="Источник не может быть пустым"
            ),

        ]

    def clean(self):
        queryset = Quote.objects.filter(source=self.source)
        if self.pk:
            queryset = queryset.exclude(pk=self.pk)
        if queryset.count() >= 3:
            raise ValidationError(
                f"Максимум 3 цитаты на источник '{self.source}'"
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def like_count(self):
        return self.votes.filter(is_like=True).count()

    def dislike_count(self):
        return self.votes.filter(is_like=False).count()


class ViewCounter(models.Model):
    quote = models.OneToOneField(Quote, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.quote} - {self.count} просмотров"


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quote = models.ForeignKey(
        Quote, on_delete=models.CASCADE, related_name='votes')
    is_like = models.BooleanField()

    class Meta:
        unique_together = ('user', 'quote')

    def __str__(self):
        return f"{self.user} {'лайкнул' if self.is_like else 'дизлайкнул'} {self.quote}"
