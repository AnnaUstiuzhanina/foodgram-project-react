from django.db import models
from django.contrib.auth.models import AbstractUser, AbstractBaseUser

class User(AbstractUser):

    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']
    USERNAME_FIELD = 'email'

    class Role(models.TextChoices): 
        guest = 'guest'
        authorized_user = 'authorized_user'
        admin = 'admin'

    email = models.EmailField(max_length=254, unique=True)
    role = models.CharField(max_length=20, choices=Role.choices,default=Role.guest)

    class Meta: 
        ordering = ['id'] 
 
    def save(self, *args, **kwargs): 
        if not self.username: 
            self.username = f'{self.email.replace(".", "")}' 
        super().save(*args, **kwargs)


class Follow(models.Model): 
    user = models.ForeignKey( 
        User, on_delete=models.CASCADE, related_name="follower" 
    ) 
    following = models.ForeignKey( 
        User, on_delete=models.CASCADE, related_name="following" 
    ) 
 
    class Meta: 
        unique_together = ('user', 'following',) 
