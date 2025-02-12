from sqlalchemy import create_engine
from sqlalchemy.sql import text

def upgrade_database():
    # Create a connection to the database
    engine = create_engine('sqlite:///instance/ecommerce.db')
    
    # Add new columns one at a time
    with engine.connect() as conn:
        statements = [
            'ALTER TABLE "order" ADD COLUMN first_name VARCHAR(100)',
            'ALTER TABLE "order" ADD COLUMN last_name VARCHAR(100)',
            'ALTER TABLE "order" ADD COLUMN address VARCHAR(200)',
            'ALTER TABLE "order" ADD COLUMN city VARCHAR(100)',
            'ALTER TABLE "order" ADD COLUMN state VARCHAR(100)',
            'ALTER TABLE "order" ADD COLUMN postal_code VARCHAR(20)',
            'ALTER TABLE "order" ADD COLUMN country VARCHAR(100)',
            'ALTER TABLE "order" ADD COLUMN phone VARCHAR(20)'
        ]
        
        for stmt in statements:
            try:
                conn.execute(text(stmt))
                conn.commit()
                print(f"Successfully executed: {stmt}")
            except Exception as e:
                print(f"Error executing {stmt}: {str(e)}")
                # Continue with other statements even if one fails
                continue

if __name__ == '__main__':
    upgrade_database()
