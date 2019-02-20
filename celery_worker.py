from blueprints import create_app, celery


app = create_app()
app.app_context().push()

@celery.task()
def add_these(x, y):
    return x + y
