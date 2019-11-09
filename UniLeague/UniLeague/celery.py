import os

from django.apps import apps

from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "UniLeague.settings")

app = Celery("UniLeague")


app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
# app.autodiscover_tasks()


app.autodiscover_tasks(lambda: [n.name for n in apps.get_app_configs()])


@app.task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))


if __name__ == "__main__":
    app.start()
