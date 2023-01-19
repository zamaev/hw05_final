from django.contrib.auth.decorators import login_required
from django.views.decorators.vary import vary_on_cookie
from django.views.decorators.cache import cache_page
from django.shortcuts import get_object_or_404, redirect, render

from core.utils import get_page_obj
from posts.forms import PostForm, CommentForm
from posts.models import User, Group, Post, Follow


@cache_page(20, key_prefix='index_page')
@vary_on_cookie
def index(request):
    page_obj = get_page_obj(request, Post.objects.all())

    return render(request, 'posts/index.html', {
        'page_obj': page_obj,
    })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    page_obj = get_page_obj(request, group.posts.all())

    return render(request, 'posts/group_list.html', {
        'group': group,
        'page_obj': page_obj,
    })


def profile(request, username):
    author = get_object_or_404(User, username=username)
    page_obj = get_page_obj(request, author.posts.all())
    context = {
        'author': author,
        'page_obj': page_obj,
    }
    if request.user.is_authenticated:
        context['following'] = request.user.follower.filter(author=author).exists()
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    return render(request, 'posts/post_detail.html', {
        'post': post,
        'form': CommentForm(),
        'comments': post.comments.all(),
    })


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user)

    return render(request, 'posts/create_post.html', {
        'form': form,
    })


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)

    return render(request, 'posts/create_post.html', {
        'form': form,
        'is_edit': True
    })


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    followings = request.user.follower.values('author_id')
    page_obj = get_page_obj(
        request,
        Post.objects.filter(author__in=followings)
    )

    return render(request, 'posts/index.html', {
        'page_obj': page_obj,
    })


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    params = {
        'user': request.user,
        'author': author,
    }
    if not Follow.objects.filter(**params).exists():
        Follow.objects.create(**params)

    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    params = {
        'user': request.user,
        'author': author,
    }
    if Follow.objects.filter(**params).exists():
        Follow.objects.get(**params).delete()

    return redirect('posts:profile', username=username)
