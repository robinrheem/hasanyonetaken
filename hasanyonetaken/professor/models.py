from django.db import models

class Professor(models.Model):
    rmp_url = models.CharField(max_length=255)
    full_name = models.CharField(max_length=100)
    university = models.CharField(max_length=200)
    department = models.CharField(max_length=100)
    ratings = models.JSONField(default=None, blank=True, null=True)
    top_tags = models.CharField(max_length=255, default=None, blank=True, null=True)
    courses = models.JSONField(default=None, blank=True, null=True)

    def __str__(self):
        return f"{self.full_name} - {self.department}"


class Review(models.Model):
    rating = models.FloatField()
    difficulty = models.FloatField()
    course = models.CharField(max_length=100)
    comment = models.TextField()
    tags = models.CharField(max_length=255)
    helpful = models.IntegerField()
    not_helpful = models.IntegerField()
    take_again = models.CharField(max_length=100, default=None, blank=True, null=True)
    for_credit = models.CharField(max_length=100, default=None, blank=True, null=True)
    has_textbook = models.CharField(max_length=100, default=None, blank=True, null=True)
    attendance_mandatory = models.CharField(max_length=100, default=None, blank=True, null=True)
    grade = models.CharField(max_length=100, default=None, blank=True, null=True)
    created_at = models.DateTimeField()
    professor = models.ForeignKey(
        Professor,
        on_delete=models.CASCADE,
        related_name="reviews"
    )
