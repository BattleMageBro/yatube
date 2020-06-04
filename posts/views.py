from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail
from .models import Post, Group, User, Comment, Follow
from .forms import PostForm, CommentForm
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required


def index(request):
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    posts = Post.objects.filter(group=group).order_by('-pub_date')[:12]
    return render(request, 'group.html', {'group': group, 'posts': posts, 'page': page, 'paginator': paginator})


@login_required
def new_post(request):
    title = 'Новая запись'
    button = 'Добавить'
    if request.method == 'POST':
        form = PostForm(request.POST or None, files=request.FILES or None)
        if form.is_valid():
            my_post = form.save(commit=False)
            my_post.author = request.user
            my_post.save()
            return redirect('index')
        return render(request, 'new.html', {'form': form})
    form = PostForm()
    return render(request, 'new.html', {'form': form, 'title': title, 'button': button})


def profile(request, username):
    user_profile = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=user_profile).order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    post_count = post_list.count()
    following = False
    follower_count = Follow.objects.filter(author=user_profile).count()
    following_count = Follow.objects.filter(user=user_profile).count()
    
    if request.user != user_profile:
        if follower_count > 0:
            following = True
    
    return render(request, 'profile.html', {'user_profile': user_profile, 'post_count': post_count, 'page': page, 'paginator': paginator, 'following': following, 'following_count': following_count, 'follower_count':follower_count})


def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    post_count = Post.objects.filter(author=post.author).count()
    author = post.author
    form = CommentForm()
    comments = Comment.objects.filter(post=post).all()
    following_count = Follow.objects.filter(user=post.author).count()
    follower_count = Follow.objects.filter(author=post.author).count()
    return render(request, 'post.html', {'user': request.user, 'author': author, 'post': post, 'post_count': post_count, 'form': form, 'comments': comments, 'following_count': following_count, 'follower_count':follower_count})


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comments = form.save(commit=False)
            comments.author = request.user
            comments.post = post
            comments.save()
            return redirect('posts', username=post.author.username, post_id=post_id)
    form = CommentForm()
    return redirect('posts', username=post.author.username, post_id=post_id)


def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    title = 'Редактировать запись'
    button = 'Сохранить'
    context = {'post': post,  'title': title, 'button': button}
    if request.user != post.author:
        return redirect('posts', username=username, post_id=post_id)
    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect(f'/{request.user.username}/{post.id}/')
    context['form'] = form
    return render(request, 'post_edit.html', context)
    

@login_required
def follow_index(request):
    favorite_list = Follow.objects.filter(user=request.user)
    author_list = [favorite.author for favorite in favorite_list]
    post_list = Post.objects.filter(author__in=author_list).order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'follow.html', {'paginator': paginator, 'page': page})

@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if Follow.objects.filter(user=request.user, author=author).count() == 0:
        if request.user != author:
            Follow.objects.create(user=request.user, author=author)
    return redirect('profile', username=author.username)

@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    to_delete = get_object_or_404(Follow, user=request.user, author=author)
    to_delete.delete()
    return redirect('profile', username=username)



def page_not_found(request, exception):
    return render(request, 'misc/404.html', {'path': request.path}, status=404)


def server_error(request):
    return render(request, 'misc/500.html', status=500)
