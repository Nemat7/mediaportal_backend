from django.contrib import admin
from .models import Category, Tag, Video, Season, Episode


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'video_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

    def video_count(self, obj):
        return obj.videos.count()
    video_count.short_description = 'Количество видео'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


class SeasonInline(admin.TabularInline):
    model = Season
    extra = 0
    show_change_link = True


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'year', 'rating', 'quality', 'views', 'is_new', 'is_popular', 'is_hero']
    list_filter = ['category', 'quality', 'is_new', 'is_popular', 'is_hero', 'year']
    search_fields = ['title', 'description', 'studio']
    filter_horizontal = ['tags']
    list_editable = ['is_new', 'is_popular', 'is_hero']
    readonly_fields = ['views', 'created_at', 'updated_at']
    inlines = [SeasonInline]
    fieldsets = (
        ('Основное', {
            'fields': ('title', 'description', 'year', 'rating', 'duration', 'quality', 'category', 'tags', 'studio')
        }),
        ('Медиа', {
            'fields': ('thumbnail', 'thumbnail_url', 'backdrop', 'backdrop_url', 'video_file', 'video_url')
        }),
        ('Флаги', {
            'fields': ('is_new', 'is_popular', 'is_hero')
        }),
        ('Статистика', {
            'fields': ('views', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class EpisodeInline(admin.TabularInline):
    model = Episode
    extra = 0
    fields = ['number', 'title', 'duration', 'video_url']


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ['video', 'number', 'title']
    list_filter = ['video']
    inlines = [EpisodeInline]


admin.site.site_header = 'Tajflix — Панель управления'
admin.site.site_title = 'Tajflix Admin'
admin.site.index_title = 'Управление контентом'
