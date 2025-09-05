from sqlalchemy import create_engine, text
from app.core.config import settings

def test_db_connection():
    try:
        # Create engine and connect
        engine = create_engine(settings.DATABASE_URL)
        
        # Test connection
        with engine.connect() as conn:
            # Check if users table exists
            result = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')"))
            users_table_exists = result.scalar()
            print(f"Users table exists: {users_table_exists}")
            
            if users_table_exists:
                # Try to fetch users
                result = conn.execute(text("SELECT * FROM users LIMIT 5"))
                users = result.fetchall()
                print(f"Found {len(users)} users in the database")
                for user in users:
                    print(f"User: {user}")
            
            # Check database version
            result = conn.execute(text("SELECT version()"))
            print(f"Database version: {result.scalar()}")
            
    except Exception as e:
        print(f"Error connecting to database: {e}")

if __name__ == "__main__":
    test_db_connection()
