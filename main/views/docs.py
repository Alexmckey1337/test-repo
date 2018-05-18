import os

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.views import View
from django.views.generic import TemplateView
from filetype import filetype

__all__ = ['DocsView']


def get_content_type(path):
    return {
        'css': 'text/css; charset=utf-8',
        'js': 'application/x-javascript',
        'woff': 'application/font-woff',
        'woff2': 'font/woff2',
        'ttf': 'font/ttf',
        'html': 'text/html',
    }.get(path.split('?', 1)[0].rsplit('.', 1)[-1], 'text/plain')


def load_docs_files(path):
    files = dict()
    for dirname, _, filenames in os.walk(path):
        dirname = dirname if dirname.endswith('/') else (dirname + '/')
        for filename in filenames:
            file_path = f'{dirname}{filename}'
            mime = filetype.guess_mime(file_path) or get_content_type(file_path)
            print(f'{mime: <30}{file_path}')
            with open(file_path, 'rb') as f:
                files[file_path] = (mime, f.read())
    return files


docs_files = load_docs_files('/app/docs/build/docs/')


class CanSeeDocsMixin(View):
    def dispatch(self, request, *args, **kwargs):
        path = kwargs.get('path', '')
        if (path == 'CHANGELOG.html' or not path.endswith('.html')) and request.user.can_see_changelog():
            return super().dispatch(request, *args, **kwargs)
        if not request.user.can_see_docs():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class DocsView(LoginRequiredMixin, CanSeeDocsMixin, TemplateView):
    login_url = 'entry'

    base_path = 'docs'
    path = 'index.html'

    def get(self, request, *args, **kwargs):
        self.path = kwargs.get('path', '')
        template = f'/app/docs/build/{self.get_template_names()}'
        mime, content = docs_files.get(template, (None, None))

        if content is None:
            print('======================= load content =======================')
            with open(template, 'rb') as f:
                content = f.read()
                docs_files[template] = (mime, content)

        content_type = mime or get_content_type(self.path)
        response = HttpResponse(content_type=content_type)
        response.write(content)
        return response

    def get_template_names(self):
        return f'{self.base_path}/{self.path}'
