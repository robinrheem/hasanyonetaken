from django.db.models import Avg
from django.shortcuts import render, get_object_or_404
from professor.models import Professor


def index(request):
    return render(request, "home.html")

def search(request):
    full_name = request.GET["full_name"]
    professor = get_object_or_404(Professor, full_name=full_name)
    mean_rating = professor.reviews.aggregate(Avg("rating"))["rating__avg"]
    mean_difficulty = professor.reviews.aggregate(Avg("difficulty"))["difficulty__avg"]
    context = {
        "professor": professor,
        "good_reviews": professor.reviews.filter(rating__gte=3.0),
        "bad_reviews": professor.reviews.filter(rating__lte=2.0),
        "mean_rating": mean_rating,
        "mean_difficulty": mean_difficulty,
    }
    return render(request, "detail.html", context)
