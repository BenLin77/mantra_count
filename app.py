from app import create_app, db
from app.models.user import User
from app.models.mantra import Mantra, MantraRecord

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Mantra': Mantra,
        'MantraRecord': MantraRecord
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
