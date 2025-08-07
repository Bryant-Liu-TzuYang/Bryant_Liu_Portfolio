
from app import create_app, db
from app.models import User, NotionDatabase, EmailSettings
import os

os.environ["FLASK_ENV"] = "development"
app = create_app()

with app.app_context():
    print("Flask shell ready! Available models: User, NotionDatabase, EmailSettings")
    print("Example queries:")
    print("  User.query.all()")
    print("  User.query.filter_by(email='your@email.com').first()")
    print("  User.query.count()")
    
    # Interactive mode
    import code
    code.interact(local=locals())
