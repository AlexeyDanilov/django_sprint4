from django.contrib import admin

from .models import Post, Category, Location


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'category',
                    'author', 'location', 'pub_date')
    list_editable = ('is_published',)
    list_display_links = ('title',)
    search_fields = ('title', 'author')
    list_filter = ('is_published', 'category', 'author', 'location')


class PostInline(admin.TabularInline):
    model = Post
    extra = 1


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'slug',)
    list_editable = ('is_published',)
    list_display_links = ('title',)
    search_fields = ('title',)
    list_filter = ('is_published',)
    inlines = (PostInline,)


class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published',)
    list_editable = ('is_published',)
    list_display_links = ('name',)
    search_fields = ('name',)
    list_filter = ('is_published',)


admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
