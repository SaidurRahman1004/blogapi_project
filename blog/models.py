from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

# Category model to categorize blog posts


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# BlogPost model to represent individual blog posts
class Post(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    content = models.TextField()
    excerpt = models.CharField(max_length=300, blank=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='draft')
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        if not self.excerpt and self.content:
            self.excerpt = self.content[:297] + '...'

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def reading_time(self):
        """Calculate reading time"""
        word_count = len(self.content.split())
        minutes = word_count // 200
        return f"{minutes} min read" if minutes > 0 else "Less than 1 min"


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"
