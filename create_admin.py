from app import app, db, User
from werkzeug.security import generate_password_hash

def create_admin():
    with app.app_context():
        # Check if admin exists
        admin = User.query.filter_by(username='admin').first()
        if admin:
            # Update existing admin password
            admin.password = generate_password_hash('admin123')
            db.session.commit()
            print("Admin password reset to: admin123")
        else:
            # Create new admin user
            admin = User(
                username='admin',
                email='admin@example.com',
                password=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")
        
        print("\nAdmin Login Details:")
        print("Username: admin")
        print("Password: admin123")

if __name__ == '__main__':
    create_admin()
