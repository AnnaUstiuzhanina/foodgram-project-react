from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (Ingredient, Recipe, RecipeFavourite, RecipeIngredient,
                     RecipeShoppingCart, Tag)
from .serializers import IngredientSerializer, RecipeSerializer, TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class FavouriteViewSet(APIView):

    def get(self, request, pk=None):
        try:
            recipe = Recipe.objects.get(id=pk)
            serializer = RecipeSerializer(
                recipe,
                context={'request': request},
            )
        except Recipe.DoesNotExist:
            return Response(
                {'error': 'Recipe does not exist'},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            RecipeFavourite.objects.get(user=request.user, recipe=recipe)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except RecipeFavourite.DoesNotExist:
            RecipeFavourite.objects.create(
                user=request.user,
                recipe=recipe
            )
            return Response(serializer.data)

    def delete(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        deleted_recipe_favouritie = RecipeFavourite.objects.filter(
                user=request.user,
                recipe=recipe
            ).delete()
        if deleted_recipe_favouritie[0] > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_404_NOT_FOUND)


class ShoppingCartViewSet(APIView):

    def get(self, request, pk=None):
        try:
            recipe = Recipe.objects.get(id=pk)
            serializer = RecipeSerializer(
                recipe,
                context={'request': request},
            )
        except Recipe.DoesNotExist:
            return Response(
                {'error': 'Recipe does not exist'},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            RecipeShoppingCart.objects.get(
                user=request.user,
                recipe=recipe
            )
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except RecipeShoppingCart.DoesNotExist:
            RecipeShoppingCart.objects.create(
                user=request.user,
                recipe=recipe
            )
            return Response(serializer.data)

    def delete(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)

        deleted_from_shopping_cart = RecipeShoppingCart.objects.filter(
                user=request.user,
                recipe=recipe
            ).delete()

        if deleted_from_shopping_cart[0] > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_404_NOT_FOUND)


class DonwloadShoppingCartViewSet(APIView):

    def get(self, request, pk=None):
        shopping_cart_relations = [ri_obj['recipe__id'] for ri_obj in RecipeShoppingCart.objects.filter(user=request.user).values('recipe__id')]
        ingredients = RecipeIngredient.objects.values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(count=Sum('amount')).filter(recipe__id__in=shopping_cart_relations)

        file_content = ''
        file_content = '\n'.join([f"{ingredient['ingredient__name']} {ingredient['count']} {ingredient['ingredient__measurement_unit']}" for ingredient in ingredients])

        response = HttpResponse(
            file_content,
            content_type='text/plain; charset=UTF-8'
        )
        response['Content-Disposition'] = ('attachment; filename=shopping_cart.txt')
        return response
