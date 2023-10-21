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
        "reviews": professor.reviews.all(),
        "mean_rating": mean_rating,
        "mean_difficulty": mean_difficulty,
    }
    return render(request, "detail.html", context)
