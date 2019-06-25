import os
import pathlib
import sys

from invoke import task

python = sys.executable
directory = os.path.dirname(__file__)
sys.path.append('src')

#
# Call python manage.py in a more robust way
#
def manage(ctx, cmd, env=None, **kwargs):
    kwargs = {k.replace('_', '-'): v for k, v in kwargs.items() if v is not False}
    opts = ' '.join(f'--{k} {"" if v is True else v}' for k, v in kwargs.items())
    cmd = f'{python} manage.py {cmd} {opts}'
    env = {**os.environ, **(env or {})}
    path = env.get("PYTHONPATH", ":".join(sys.path))
    env.setdefault('PYTHONPATH', f'src:{path}')
    ctx.run(cmd, pty=True, env=env)


@task
def run(ctx):
    """
    Run development server.
    """
    env = {}
    manage(ctx, 'runserver 0.0.0.0:8000', env)


@task
def db(ctx, migrate_only=False):
    """
    Perform migrations.
    """
    if not migrate_only:
        manage(ctx, 'makemigrations')
    manage(ctx, 'migrate')
