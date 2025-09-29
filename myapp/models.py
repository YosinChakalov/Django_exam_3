import datetime
from django.db import models


class User(models.Model):
    username = models.CharField(max_length=50,unique=True)
    password = models.CharField(max_length=50)

    def __str__(self):
        return self.username
    
class Project(models.Model):
    title = models.CharField(max_length=100)
    desc = models.TextField(blank=True,null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    updated_at = models.DateField(auto_now_add=True)        
    is_deleted = models.BooleanField(default=False)

    def delete(self):
        self.is_deleted = True
        self.save()

    def restore(self):
        self.is_deleted = False
        self.save()

    def __str__(self):
        return self.title
    
class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    desc = models.TextField(blank=True,null=True)
    priority = models.IntegerField()
    created_at = models.DateField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    def delete(self):
        self.is_deleted = True
        self.save()

    def restore(self):
        self.is_deleted = False
        self.save()

    def __str__(self):
        return self.title