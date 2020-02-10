from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import BlogPost

from .forms import PostForm


def post_list(request):
    posts = BlogPost.objects.filter(published_date__lte=timezone.now()).order_by(
        "published_date"
    )
    return render(request, "blog/post_list.html", {"posts": posts})


def post_detail(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    return render(request, "blog/post_detail.html", {"post": post})


def post_new(request):
    form = PostForm()
    return render(request, "blog/post_edit.html", {"form": form})
