from django.db import models

class Objective(models.Model):
    name = models.CharField(max_length=255, verbose_name="??? ?????")
    description = models.TextField(verbose_name="??? ?????")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="????? ???????")

    def __str__(self):
        return self.name

class CommandLog(models.Model):
    objective = models.ForeignKey(Objective, on_delete=models.CASCADE, verbose_name="?????")
    command = models.TextField(verbose_name="?????")
    result = models.TextField(verbose_name="???????")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="????? ???????")

    def __str__(self):
        return f"{self.objective.name} - {self.command}"
