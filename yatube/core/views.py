from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import RedirectView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import ListView
from django.shortcuts import render

from posts.models import User, Follow


def page_not_found(request, exception):
    return render(request, 'core/404.html', {'path': request.path}, status=404)


def server_error(request):
    return render(request, 'core/500.html', status=500)


def permission_denied(request, exception):
    return render(request, 'core/403.html', status=403)


def csrf_failure(request, reason=''):
    return render(request, 'core/403csrf.html')


class DetailListView(SingleObjectMixin, ListView):
    paginate_by = settings.POSTS_PER_PAGE
    general_object_model = None
    relate_list_name = None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(self.general_object_model.objects.all())
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return getattr(self.object, self.relate_list_name).all()


class FollowView(
    LoginRequiredMixin, SingleObjectMixin, RedirectView
):
    model = User
    slug_field = 'username'
    slug_url_kwarg = 'username'
    pattern_name = 'posts:profile'

    def get_params(self):
        return {
            'user': self.request.user,
            'author': self.get_object(),
        }

    def follow(self):
        if self.request.user != self.get_object():
            if not Follow.objects.filter(**self.get_params()).exists():
                Follow.objects.create(**self.get_params())

    def unfollow(self):
        if self.request.user != self.get_object():
            if Follow.objects.filter(**self.get_params()).exists():
                Follow.objects.get(**self.get_params()).delete()
