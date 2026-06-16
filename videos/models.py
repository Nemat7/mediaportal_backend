from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField('Название', max_length=100)
    slug = models.SlugField('Слаг', unique=True)
    description = models.TextField('Описание', blank=True)
    icon = models.CharField('Иконка', max_length=10, blank=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(models.Model):
    name = models.CharField('Название', max_length=50)
    slug = models.SlugField('Слаг', unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Video(models.Model):
    QUALITY_CHOICES = [('4K', '4K'), ('HD', 'HD'), ('SD', 'SD')]

    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)
    year = models.IntegerField('Год')
    rating = models.DecimalField('Рейтинг', max_digits=3, decimal_places=1, default=0)
    duration = models.CharField('Длительность', max_length=20)
    quality = models.CharField('Качество', max_length=5, choices=QUALITY_CHOICES, default='HD')

    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='Категория', related_name='videos'
    )
    tags = models.ManyToManyField(Tag, blank=True, verbose_name='Теги')

    thumbnail = models.ImageField('Миниатюра', upload_to='thumbnails/', blank=True)
    backdrop = models.ImageField('Задний фон', upload_to='backdrops/', blank=True)
    thumbnail_url = models.URLField('URL миниатюры', blank=True)
    backdrop_url = models.URLField('URL заднего фона', blank=True)

    video_file = models.FileField('Видео файл', upload_to='videos/', blank=True)
    video_url = models.URLField('URL видео', blank=True)
    bunny_video_id = models.CharField('Bunny Stream Video ID', max_length=100, blank=True)

    views = models.PositiveIntegerField('Просмотры', default=0)
    studio = models.CharField('Студия', max_length=100, blank=True)

    is_new = models.BooleanField('Новинка', default=False)
    is_popular = models.BooleanField('Популярное', default=False)
    is_hero = models.BooleanField('Показать в слайдере', default=False)

    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Видео'
        verbose_name_plural = 'Видео'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.year})'

    def get_thumbnail(self):
        if self.thumbnail:
            return self.thumbnail.url
        return self.thumbnail_url

    def get_backdrop(self):
        if self.backdrop:
            return self.backdrop.url
        return self.backdrop_url


class Season(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='seasons', verbose_name='Сериал')
    number = models.PositiveIntegerField('Номер сезона')
    title = models.CharField('Название', max_length=200, blank=True)

    class Meta:
        verbose_name = 'Сезон'
        verbose_name_plural = 'Сезоны'
        ordering = ['number']
        unique_together = ['video', 'number']

    def __str__(self):
        return f'{self.video.title} — Сезон {self.number}'


class Episode(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='episodes', verbose_name='Сезон')
    number = models.PositiveIntegerField('Номер эпизода')
    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)
    duration = models.CharField('Длительность', max_length=20, blank=True)
    thumbnail_url = models.URLField('URL миниатюры', blank=True)
    video_file = models.FileField('Видео файл', upload_to='episodes/', blank=True)
    video_url = models.URLField('URL видео', blank=True)

    class Meta:
        verbose_name = 'Эпизод'
        verbose_name_plural = 'Эпизоды'
        ordering = ['number']
        unique_together = ['season', 'number']

    def __str__(self):
        return f'{self.season} — Эп. {self.number}: {self.title}'
