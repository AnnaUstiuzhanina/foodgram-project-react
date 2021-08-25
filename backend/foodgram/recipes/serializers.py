from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from users.serializers import FullUserSerializer

from .models import (Ingredient, Recipe, RecipeFavourite, RecipeIngredient,
                     RecipeShoppingCart, Tag)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id'
    )
    amount = serializers.IntegerField()

    class Meta:
        fields = ('id', 'amount')
        model = RecipeIngredient


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
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=False,
        queryset=Tag.objects.all()
    )
    is_favorited = serializers.SerializerMethodField('check_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        'check_is_in_shopping_cart'
    )

    def create_recipe_ingredients(self, recipe, ingredients_data):
        for ingredient in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient['ingredient']['id'],
                amount=ingredient['amount'],
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

        # for attr, value in validated_data.items():
        #     setattr(instance, attr, value)

        # instance.save()

        RecipeIngredient.objects.filter(recipe=instance).delete()
        self.create_recipe_ingredients(instance, ingredients_data)
        instance.tags.set(tags)

        return super().update(instance, validated_data)

    def check_is_favorited(self, obj):
        if self.context['request'].user.is_anonymous:
            return False

        if RecipeFavourite.objects.filter(
            recipe=obj,
            user=self.context['request'].user
        ):
            return True
        return False

    def check_is_in_shopping_cart(self, obj):
        if self.context['request'].user.is_anonymous:
            return False

        if RecipeShoppingCart.objects.filter(
            recipe=obj,
            user=self.context['request'].user
        ):
            return True
        return False

    class Meta:
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart'
        )
        model = Recipe
        read_only_fields = ('author', 'is_favorited', 'is_in_shopping_cart')


class RecipeFavouriteSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('recipe', 'user')
        model = RecipeFavourite
