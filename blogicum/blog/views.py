from django.db.models import Count
from django.http import Http404
from django.views.generic import (
    ListView, DetailView, CreateView, DeleteView
)
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.views.generic import UpdateView
from .models import Post, Category, Comment
from .forms import PostEditForm, CommentEditForm, CommentForm, UserEditForm
from .mixins import OnlyAuthorMixin


User = get_user_model()
POSTS_ON_PAGE = 10


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'page_obj'
    paginate_by = POSTS_ON_PAGE

    def get_queryset(self):
        return Post.objects.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        ).annotate(
            comment_count=Count('comments')
        ).select_related(
            'category', 'author', 'location'
        ).order_by('-pub_date')


class CategoryPostsView(ListView):
    template_name = 'blog/category.html'
    context_object_name = 'page_obj'
    paginate_by = POSTS_ON_PAGE

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return Post.objects.filter(
            category=self.category,
            is_published=True,
            pub_date__lte=timezone.now()
        ).annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        return super().get_queryset().filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        all_comments = self.object.comments.all()
        context['comments'] = all_comments .select_related('author')
        return context

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])

        if self.request.user == post.author:
            return post

        if (post.is_published and post.category.is_published
                and post.pub_date <= timezone.now()):
            return post

        raise Http404("Пост не найден или недоступен")


# Пользовательские представления
class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/registration_form.html'
    success_url = reverse_lazy('login')


class ProfileView(ListView):
    template_name = 'blog/profile.html'
    context_object_name = 'page_obj'
    paginate_by = POSTS_ON_PAGE

    def get_queryset(self):
        self.profile_user = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        queryset = Post.objects.filter(author=self.profile_user)

        if self.request.user != self.profile_user:
            queryset = queryset.filter(
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now()
            )
        return queryset.annotate(
            comment_count=Count('comments')).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.profile_user
        context['posts_count'] = self.get_queryset().count()
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    form_class = UserEditForm
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        """Переадресация."""
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


# Работа с постами
class CreatePostView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostEditForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


class DeletePostView(OnlyAuthorMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse('blog:index')


# Работа с комментариями
class AddCommentView(LoginRequiredMixin, CreateView):
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['pk'])
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Переадресация."""
        return reverse('blog:post_detail',
                       kwargs={'pk': self.kwargs.get('pk')})


class EditCommentView(LoginRequiredMixin, UpdateView):
    form_class = CommentEditForm
    template_name = 'blog/comment.html'

    def get_object(self):
        return get_object_or_404(
            Comment,
            pk=self.kwargs['comment_id'],
            author=self.request.user
        )

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'pk': self.kwargs.get('pk')})


class DeleteCommentView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def test_func(self):
        author = self.get_object().author
        return self.request.user == author or self.request.user.is_staff

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'pk': self.kwargs.get('pk')})


class EditPostView(OnlyAuthorMixin, UpdateView):
    model = Post
    form_class = PostEditForm
    template_name = 'blog/create.html'
    context_object_name = 'post'

    def get_queryset(self):
        return super().get_queryset().filter(author=self.request.user)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.object.pk})

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs["pk"])
        if self.request.user != post.author:
            return redirect("blog:post_detail", pk=self.kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)
