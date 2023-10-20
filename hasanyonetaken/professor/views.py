from django.shortcuts import render


def index(request):
    return render(request, "home.html")


def detail(request, id):
    # TODO: Get professor detail information from database
    # and populate to context
    context = {
        "id": id,
    }
    return render(request, "detail.html", context)
