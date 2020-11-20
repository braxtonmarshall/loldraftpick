from __future__ import absolute_import
import os
from celery import Celery

# set default Django setting module for 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'loldraft.settings')
app = Celery('loldraft')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


def rate_limit(task, task_group):
    with task.app.connection_for_read() as conn:
        msg = conn.default_channel.basic_get(task_group + '_token', no_ack=True)
        if msg is None:
            task.retry(countdown=1.25)


@app.task
def token():
    return 1


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task((1.25, token.signature(queue='loldraft_token')))
