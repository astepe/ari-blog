import sys
import os
sys.path.append(os.getcwd())
from blueprints import create_app, db
from blueprints.models import BlogPost, Project

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'blogpost': BlogPost, 'project': Project}


if __name__ == '__main__':
    app.run(debug=True)
