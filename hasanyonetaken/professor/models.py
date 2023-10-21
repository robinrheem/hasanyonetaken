from django.db import models

class Professor(models.Model):
    full_name = models.CharField(max_length=100)
    university = models.CharField(max_length=200)
    department = models.CharField(max_length=100)
    ratings = models.JSONField()
    top_tags = models.CharField(max_length=255)
    courses = models.JSONField()


class Review(models.Model):
    rating = models.IntegerField()
    difficulty = models.IntegerField()
    course = models.CharField(max_length=100)
    comment = models.TextField()
    tags = models.CharField(max_length=255)
    helpful = models.IntegerField()
    not_helpful = models.IntegerField()
    take_again = models.BooleanField()
    for_credit = models.BooleanField()
    has_textbook = models.BooleanField()
    attendance_mandatory = models.BooleanField()
    grade = models.FloatField()
    created_at = models.DateTimeField()
    professor = models.ForeignKey(
        Professor,
        on_delete=models.CASCADE,
        related_name="reviews"
    )
