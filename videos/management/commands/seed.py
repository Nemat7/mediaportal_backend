from django.core.management.base import BaseCommand
from videos.models import Category, Tag, Video

IMGS = [
    "1536440136628-849c177e76a1", "1626814026160-2237a95fc5a0", "1440404653325-ab127d49abc1",
    "1446776811953-b23d57bd21aa", "1478720568477-152d9b164e26", "1485846234645-a62644f84728",
    "1489599849927-2ee91cede3ba", "1524985069026-dd778a71c7b4", "1509347528160-9a9e33742cdb",
    "1611523658822-385aa008324c",
]

def T(i): return f"https://images.unsplash.com/photo-{IMGS[i % 10]}?w=480&q=80"
def B(i): return f"https://images.unsplash.com/photo-{IMGS[(i + 4) % 10]}?w=1280&q=80"

CATEGORIES = [
    ('Кино', 'kino'), ('Сериалы', 'serialy'), ('Комедия', 'comedy'),
    ('Боевик', 'boevik'), ('Подкасты', 'podcasts'), ('Шоу', 'show'), ('Клипы', 'clips'),
]

VIDEOS = [
    # kino
    dict(title='Дорога домой', year=2023, rating='8.5', duration='1:45', quality='4K', category='kino', studio='Таджикфильм', is_hero=True, is_popular=True, views=212000),
    dict(title='Горный орёл', year=2022, rating='7.9', duration='1:52', quality='HD', category='kino', studio='МедиаГрупп', is_popular=True, views=98000),
    dict(title='Последний перевал', year=2023, rating='8.1', duration='2:05', quality='4K', category='kino', studio='Таджикфильм', is_new=True, views=76000),
    dict(title='Сердце Памира', year=2021, rating='7.5', duration='1:38', quality='HD', category='kino', studio='ТВТаджик', views=54000),
    dict(title='Сыновья земли', year=2022, rating='8.3', duration='1:56', quality='HD', category='kino', studio='Таджикфильм', is_hero=True, is_popular=True, views=183000),
    # serialy
    dict(title='Семья', year=2023, rating='8.7', duration='45 мин', quality='HD', category='serialy', studio='ТВТаджик', is_hero=True, is_new=True, views=320000),
    dict(title='Братья', year=2022, rating='8.2', duration='50 мин', quality='HD', category='serialy', studio='МедиаГрупп', is_popular=True, views=210000),
    dict(title='Столица', year=2023, rating='7.8', duration='40 мин', quality='4K', category='serialy', studio='ТВТаджик', is_new=True, views=145000),
    dict(title='Возвращение', year=2021, rating='8.0', duration='48 мин', quality='HD', category='serialy', studio='Таджикфильм', is_popular=True, views=178000),
    dict(title='Доверие', year=2022, rating='7.6', duration='42 мин', quality='HD', category='serialy', studio='МедиаГрупп', views=98000),
    # comedy
    dict(title='Мастчони', year=2023, rating='8.7', duration='1:30', quality='HD', category='comedy', studio='Comedy.tj', is_popular=True, is_new=True, views=560000),
    dict(title='Весёлые соседи', year=2022, rating='7.4', duration='1:25', quality='HD', category='comedy', studio='Comedy.tj', views=234000),
    dict(title='Базарный день', year=2023, rating='7.9', duration='1:35', quality='HD', category='comedy', studio='Comedy.tj', is_new=True, views=198000),
    dict(title='Свадьба в Кулябе', year=2021, rating='7.2', duration='1:40', quality='HD', category='comedy', studio='ТВТаджик', is_popular=True, views=312000),
    dict(title='Три товарища', year=2022, rating='7.6', duration='1:28', quality='HD', category='comedy', studio='Comedy.tj', views=145000),
    # boevik
    dict(title='Пограничник', year=2023, rating='8.3', duration='1:55', quality='4K', category='boevik', studio='ActionFilm', is_hero=True, is_new=True, is_popular=True, views=410000),
    dict(title='Рейд', year=2022, rating='7.8', duration='1:48', quality='HD', category='boevik', studio='ActionFilm', is_popular=True, views=287000),
    dict(title='Красная линия', year=2023, rating='8.1', duration='2:02', quality='4K', category='boevik', studio='МедиаГрупп', is_new=True, views=198000),
    dict(title='Последний бой', year=2021, rating='7.5', duration='1:52', quality='HD', category='boevik', studio='ActionFilm', views=156000),
    dict(title='Тень гор', year=2022, rating='7.9', duration='1:45', quality='HD', category='boevik', studio='ActionFilm', is_popular=True, views=223000),
    # podcasts
    dict(title='Навои вакт', year=2023, rating='8.0', duration='1:10', quality='HD', category='podcasts', studio='PodcastTJ', is_new=True, is_popular=True, views=89000),
    dict(title='Технологии будущего', year=2023, rating='7.8', duration='58 мин', quality='HD', category='podcasts', studio='PodcastTJ', is_new=True, views=67000),
    dict(title='Бизнес по-таджикски', year=2022, rating='7.5', duration='1:15', quality='HD', category='podcasts', studio='MediaHub', views=45000),
    dict(title='Здоровье и спорт', year=2023, rating='7.2', duration='45 мин', quality='HD', category='podcasts', studio='PodcastTJ', views=38000),
    dict(title='История Таджикистана', year=2022, rating='8.3', duration='1:20', quality='HD', category='podcasts', studio='MediaHub', is_popular=True, views=112000),
    # show
    dict(title='Истеъдод', year=2023, rating='8.5', duration='1:30', quality='HD', category='show', studio='ShowTJ', is_hero=True, is_new=True, is_popular=True, views=678000),
    dict(title='Кулминация', year=2023, rating='7.9', duration='1:25', quality='HD', category='show', studio='ShowTJ', is_new=True, views=234000),
    dict(title='Миллион мечтаний', year=2022, rating='8.1', duration='1:35', quality='HD', category='show', studio='MediaHub', is_popular=True, views=345000),
    dict(title='Поварское шоу', year=2023, rating='7.6', duration='48 мин', quality='HD', category='show', studio='ShowTJ', is_new=True, views=123000),
    dict(title='Таджикская звезда', year=2022, rating='8.4', duration='1:20', quality='HD', category='show', studio='ShowTJ', is_popular=True, views=456000),
    # clips
    dict(title='Суруди нав', year=2023, rating='7.8', duration='4:25', quality='HD', category='clips', studio='MusicTJ', is_new=True, is_popular=True, views=1200000),
    dict(title='Дилам мехохад', year=2023, rating='8.2', duration='3:50', quality='4K', category='clips', studio='ClipZone', is_new=True, is_hero=True, views=890000),
    dict(title='Ватан', year=2022, rating='8.5', duration='5:10', quality='HD', category='clips', studio='MusicTJ', is_popular=True, views=2100000),
    dict(title='Бахор омад', year=2023, rating='7.5', duration='3:30', quality='HD', category='clips', studio='ClipZone', is_new=True, views=456000),
    dict(title='Ишки ман', year=2022, rating='7.9', duration='4:05', quality='HD', category='clips', studio='MusicTJ', is_popular=True, views=780000),
]


class Command(BaseCommand):
    help = 'Seed database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Создание категорий...')
        cats = {}
        for name, slug in CATEGORIES:
            cat, _ = Category.objects.get_or_create(slug=slug, defaults={'name': name})
            cats[slug] = cat

        self.stdout.write('Создание видео...')
        for i, v in enumerate(VIDEOS):
            cat = cats.get(v.pop('category'))
            Video.objects.get_or_create(
                title=v['title'],
                year=v['year'],
                defaults={
                    **v,
                    'category': cat,
                    'thumbnail_url': T(i),
                    'backdrop_url': B(i),
                    'description': f"Увлекательный контент от студии {v.get('studio', '')}. Смотрите онлайн на Tajflix.",
                }
            )

        self.stdout.write(self.style.SUCCESS(
            f'Готово: {Category.objects.count()} категорий, {Video.objects.count()} видео'
        ))
