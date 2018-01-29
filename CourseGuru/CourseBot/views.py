from django.views.generic.base import TemplateView


class Bot(TemplateView):
    template_name = "bot.html"