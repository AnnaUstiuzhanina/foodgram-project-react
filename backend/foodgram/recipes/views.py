from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Sum
from django.http import HttpResponse
from wsgiref.util import FileWrapper

from .models import Recipe, Ingredient, RecipeIngredient, Tag, RecipeFavourite, RecipeShoppingCart
from .serializers import RecipeSerializer, IngredientSerializer, RecipeIngredientSerializer, TagSerializer

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

    @action(detail=True, methods=['get', 'delete'], permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        
        try:
            recipe = Recipe.objects.get(id=pk)
            serializer = self.get_serializer(recipe)
        except Recipe.DoesNotExist:
            return Response(
                {'error': 'Recipe does not exist'},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        if request.method == 'GET':
            try:
                RecipeFavourite.objects.get(user=request.user, recipe=recipe)
                return Response(status=status.HTTP_400_BAD_REQUEST)
            except RecipeFavourite.DoesNotExist:
                RecipeFavourite.objects.create(user=request.user, recipe=recipe)
                return Response(serializer.data)

        elif request.method == 'DELETE':
            try:
                RecipeFavourite.objects.get(user=request.user, recipe=recipe)
                RecipeFavourite.objects.filter(user=request.user, recipe=recipe).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except RecipeFavourite.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)


    @action(detail=True, methods=['get', 'delete'], permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        
        try:
            recipe = Recipe.objects.get(id=pk)
            serializer = self.get_serializer(recipe)
        except Recipe.DoesNotExist:
            return Response(
                {'error': 'Recipe does not exist'},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        if request.method == 'GET':
            try:
                RecipeShoppingCart.objects.get(user=request.user, recipe=recipe)
                return Response(status=status.HTTP_400_BAD_REQUEST)
            except RecipeShoppingCart.DoesNotExist:
                RecipeShoppingCart.objects.create(user=request.user, recipe=recipe)
                return Response(serializer.data)

        elif request.method == 'DELETE':
            try:
                RecipeShoppingCart.objects.get(user=request.user, recipe=recipe)
                RecipeShoppingCart.objects.filter(user=request.user, recipe=recipe).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except RecipeShoppingCart.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request, pk=None):
        shopping_cart_relations = [ri_obj['recipe__id'] for ri_obj in RecipeShoppingCart.objects.filter(user=request.user).values('recipe__id')]
        ingredients = RecipeIngredient.objects.values('ingredient__name', 'ingredient__measurement_unit').annotate(count=Sum('amount')).filter(recipe__id__in=shopping_cart_relations)
        file_content = ''

        for ingredient in ingredients:
            file_content = f"{ingredient['ingredient__name']} {ingredient['ingredient__measurement_unit']} {ingredient['count']}\n"
        
        response = HttpResponse(file_content, content_type='text/plain; charset=UTF-8')
        response['Content-Disposition'] = ('attachment; filename=shopping_cart.txt')
        return response

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


RecipeIngredient.objects.values('ingredient__name', 'ingredient__measurement_unit').annotate(count=Sum('amount')).filter(recipe__id__in=[])

