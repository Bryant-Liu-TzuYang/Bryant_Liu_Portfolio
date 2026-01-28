
from app.models import User, NotionDatabase, NotionToken, EmailService, EmailLog
from application import app  # Reuse the app creation from application.py

import os

os.environ["FLASK_ENV"] = "development"

with app.app_context():
    print("Flask shell ready! Available models: User, NotionDatabase, NotionToken, EmailService, EmailLog")
    print("Example queries:")
    print("  User.query.all()")
    print("  User.query.filter_by(email='your@email.com').first()")
    print("  User.query.count()")
    
    # Interactive mode
    import code
    code.interact(local=locals())
