from django.core.validators import MinValueValidator
from django.db import models
from users.models import User


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор рецепта',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='название рецепта',
    )
    image = models.ImageField(
        upload_to='recipe_images',
        verbose_name='фото блюда',
    )
    text = models.CharField(
        max_length=200,
        verbose_name='описание рецепта',
    )
    tags = models.ManyToManyField(
        'Tag',
        verbose_name='теги рецепта',
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), ],
        verbose_name='время готовки',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='название ингредиента',
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='единица измерения',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='количество ингредиента',
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='название тега',
    )
    color = models.CharField(
        max_length=200,
        verbose_name='цвет тега'
    )
    slug = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='уникальное название тега',
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class RecipeFavourite(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favourite',
        verbose_name='рецепт',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='пользователь',
    )

    class Meta:
        verbose_name = 'Рецепт в избранном'
        verbose_name_plural = 'Рецепты в избранном'


class RecipeShoppingCart(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='рецепт',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='пользователь',
    )

    class Meta:
        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзине'
