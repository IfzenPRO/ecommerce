from app import app, db

def migrate():
    with app.app_context():
        # Add is_active column
        db.session.execute('ALTER TABLE user ADD COLUMN is_active BOOLEAN DEFAULT TRUE')
        db.session.commit()
        print("Added is_active column to user table")

if __name__ == '__main__':
    migrate()
