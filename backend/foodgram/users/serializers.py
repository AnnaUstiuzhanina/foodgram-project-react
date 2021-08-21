from django.contrib.auth import get_user_model 
from rest_framework import serializers 
from .models import User, Follow
from recipes.models import Recipe
from rest_framework.validators import UniqueTogetherValidator 
from djoser.serializers import UserSerializer as DjoserUserSerializer

User = get_user_model() 


class FullUserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField('check_is_subscribed', read_only=True)

    def check_is_subscribed(self, obj):
        print(self.context['request'].user, obj)
        if self.context['request'].user.is_anonymous:
            return False

        if self.context['request'].user == obj:
            return True

        if Follow.objects.filter(following=self.context['request'].user, user=obj):
            return True
        return False

    class Meta:
        model = User
        fields = list(DjoserUserSerializer.Meta.fields) + ['is_subscribed']
        read_only_fields = list(DjoserUserSerializer.Meta.read_only_fields) +  ['is_subscribed']


class RecipeCountFollowUserField(serializers.Field):
    def get_attribute(self, instance):
        return Recipe.objects.filter(author=instance.following)

    def to_representation(self, recipe_list):     
        return recipe_list.count()


class RecipeFollowUserField(serializers.Field):
    def get_attribute(self, instance):
        print(Recipe.objects.filter(author=instance.following))
        return Recipe.objects.filter(author=instance.following)

    def to_representation(self, recipe_list):
        print(recipe_list)
        recipe_data = []
        for recipe in recipe_list:
            recipe_data.append(
                {
                    "id": recipe.id,
                    "name": recipe.name,
                    "image": recipe.image.url,
                    "cooking_time": recipe.cooking_time,
                }
            )       
        return recipe_data


class FollowUsersSerializer(serializers.ModelSerializer): 
    email = serializers.ReadOnlyField(source='following.email')
    id = serializers.ReadOnlyField(source='following.id')
    username = serializers.ReadOnlyField(source='following.username')
    first_name = serializers.ReadOnlyField(source='following.first_name')
    last_name = serializers.ReadOnlyField(source='following.last_name')
    is_subscribed = serializers.ReadOnlyField(default=True)
    recipes = RecipeFollowUserField()
    recipes_count = RecipeCountFollowUserField()
    
    class Meta:
        read_only_fields = (
            'email', 
            'id', 
            'username', 
            'first_name', 
            'last_name', 
            'is_subscribed', 
            'recipes',
            'recipes_count',
        )
        fields = (
            'email', 
            'id', 
            'username', 
            'first_name', 
            'last_name', 
            'is_subscribed', 
            'recipes',
            'recipes_count',
        )
        model = Follow



# class FollowSerializer(serializers.ModelSerializer): 
#     user = serializers.SlugRelatedField( 
#         slug_field='username', 
#         read_only=True, 
#         default=serializers.CurrentUserDefault() 
#     ) 
#     following = serializers.SlugRelatedField( 
#         slug_field='username', 
#         queryset=User.objects.all() 
#     ) 
 
#     def validate_following(self, value): 
#         user = self.context['request'].user 
#         following = get_object_or_404(User, username=value) 
#         if user == following: 
#             raise serializers.ValidationError('Невозможно подписаться.') 
#         return value 
 
#     class Meta: 
#         fields = '__all__' 
#         model = Follow 
 
#         validators = [ 
#             UniqueTogetherValidator( 
#                 queryset=Follow.objects.all(), 
#                 fields=['user', 'following'], 
#                 message='Вы уже подписаны.', 
#             ) 
#         ] 
 