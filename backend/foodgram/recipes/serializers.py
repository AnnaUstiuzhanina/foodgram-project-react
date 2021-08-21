from rest_framework import serializers 
 
from .models import Recipe, Ingredient, Tag, RecipeIngredient, RecipeFavourite, RecipeShoppingCart
from users.serializers import FullUserSerializer

import base64, uuid
from django.core.files.base import ContentFile
from drf_extra_fields.fields import Base64ImageField


# class Base64ImageField(serializers.ImageField):
#     def from_native(self, data):
#         if isinstance(data, basestring) and data.startswith('data:image'):
#             # base64 encoded image - decode
#             format, imgstr = data.split(';base64,')  # format ~= data:image/X,
#             ext = format.split('/')[-1]  # guess file extension

#             data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

#         return super(Base64ImageField, self).from_native(data)

# # Custom image field - handles base 64 encoded images
# class Base64ImageField(serializers.ImageField):
#     def to_internal_value(self, data):
#         if isinstance(data, str) and data.startswith('data:image'):
#             # base64 encoded image - decode
#             format, imgstr = data.split(';base64,') # format ~= data:image/X,
#             ext = format.split('/')[-1] # guess file extension
#             id = uuid.uuid4()
#             data = ContentFile(base64.b64decode(imgstr), name = id.urn[9:] + '.' + ext)
#         return super(Base64ImageField, self).to_internal_value(data)

#     def to_representation(self, value):
#         print(value)
#         return True


class IngredientSerializer(serializers.ModelSerializer): 
    class Meta: 
        fields = ('id', 'name', 'measurement_unit') 
        model = Ingredient


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all(), source='ingredient.id')
    amount = serializers.IntegerField()
    class Meta:
        fields = ('id', 'amount')
        model = RecipeIngredient


# class MixedIngredientSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     amount = serializers.IntegerField()


class TagSerializer(serializers.ModelSerializer): 
    class Meta: 
        fields = ('id', 'name', 'color', 'slug') 
        model = Tag


class RecipeTagSerializer(serializers.ModelSerializer):

    def to_representation(self, value):
         return value.id

    class Meta:
        model = Tag
        fields = ('id',) 


class RecipeSerializer(serializers.ModelSerializer): 
    author = FullUserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = RecipeIngredientSerializer(required=True, many=True)
    tags = serializers.PrimaryKeyRelatedField(many=True,\
                read_only=False, queryset=Tag.objects.all())
    is_favorited = serializers.SerializerMethodField('check_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField('check_is_in_shopping_cart')

    def create_recipe_ingredients(self, recipe, ingredients_data):
        for ingredient in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient['ingredient']['id'],
                amount = ingredient['amount'],
            )

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_recipe_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data): 
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        RecipeIngredient.objects.filter(recipe=instance).delete()
        self.create_recipe_ingredients(instance, ingredients_data)

        instance.tags.set(tags)
        
        return instance

    
    def check_is_favorited(self, obj):
        if self.context['request'].user.is_anonymous:
            return False

        if RecipeFavourite.objects.filter(recipe=obj, user=self.context['request'].user):
            return True
        return False

    def check_is_in_shopping_cart(self, obj):
        if self.context['request'].user.is_anonymous:
            return False

        if RecipeShoppingCart.objects.filter(recipe=obj, user=self.context['request'].user):
            return True
        return False

    class Meta: 
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'image', 'text', 'cooking_time', 'is_favorited', 'is_in_shopping_cart') 
        model = Recipe
        read_only_fields = ('author','is_favorited', 'is_in_shopping_cart')


class RecipeFavouriteSerializer(serializers.ModelSerializer):
    class Meta: 
        fields = ('recipe', 'user') 
        model = RecipeFavourite