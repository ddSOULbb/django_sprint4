from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator

User = get_user_model()


class PublishedModel(models.Model):
    """Абстрактная модель с полями is_published и created_at."""

    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)

    class Meta:
        abstract = True


class Category(PublishedModel):
    title = models.CharField('Заголовок', max_length=256)
    description = models.TextField('Описание')
    slug = models.SlugField(
        'Идентификатор',
        unique=True,
        help_text='Идентификатор страницы для URL; '
                  'разрешены символы латиницы, цифры, дефис и подчёркивание.'
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(PublishedModel):
    name = models.CharField('Название места', max_length=256)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(PublishedModel):
    title = models.CharField('Заголовок', max_length=256)
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text='Если установить дату и время в будущем —'
                  ' можно делать отложенные публикации.'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория'
    )
    image = models.ImageField(
        'Изображение',
        upload_to='posts/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])],
        help_text='Загрузите изображение (JPG/PNG)'
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.title


class Comment(models.Model):
    text = models.TextField(verbose_name="Комментарий")
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name="Пост",
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор"
    )
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name="Добавлено")

    class Meta:
        verbose_name = "комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ("created_at", 'text')

    def __str__(self):
        return self.text
