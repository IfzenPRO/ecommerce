from app import app, db, User

def reactivate_admin():
    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        if admin:
            admin.is_active = True
            db.session.commit()
            print("Admin account has been reactivated!")
        else:
            print("Admin account not found!")

if __name__ == '__main__':
    reactivate_admin()
