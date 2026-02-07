from rest_framework import serializers
from django.contrib.auth.models import User
from blog.models import Category, Post, Comment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password',
                  'password2', 'first_name', 'last_name']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user


# Catagory Serializer
class CategorySerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug',
                  'description', 'post_count', 'created_at']
        read_only_fields = ['slug']

        def get_post_count(self, obj):
            return obj.posts.filter(status='published').count()
# Comment Serializer


class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(
        source='author.username', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'author_username',
                  'content', 'created_at', 'updated_at']
        read_only_fields = ['author']
# Post Serializer


class PostSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(
        source='author.username', read_only=True)
    category_name = serializers.CharField(
        source='category.name', read_only=True)
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'excerpt',
            'author', 'author_username',
            'category', 'category_name',
            'status', 'image', 'view_count',
            'comment_count', 'created_at'
        ]

    def get_comment_count(self, obj):
        return obj.comments.count()


class PostDetailSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    reading_time = serializers.CharField(read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'content', 'excerpt',
            'author', 'category', 'status', 'image',
            'view_count', 'reading_time', 'comments',
            'created_at', 'updated_at'
        ]


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'category', 'status', 'image']

    def validate_title(self, value):
        if len(value) < 20:
            raise serializers.ValidationError(
                "Title must be at least 20 characters long.")
        return value
