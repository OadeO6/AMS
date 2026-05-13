# scripts/create_admin.py
import asyncio
import sys
import os

# Add src to path so we can import app modules
sys.path.append(os.path.join(os.getcwd(), "src"))

from app.core.database import AsyncSessionFactory
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from sqlalchemy import select

async def create_admin(email, password):
    async with AsyncSessionFactory() as session:
        # Check if user exists
        res = await session.execute(select(User).where(User.email == email))
        if res.scalar_one_or_none():
            print(f"Error: User with email {email} already exists.")
            return

        admin = User(
            email=email,
            hashed_password=get_password_hash(password),
            first_name="System",
            last_name="Admin",
            roles=[UserRole.ADMIN.value],
            is_active=True,
        )
        session.add(admin)
        await session.commit()
        print(f"Successfully created admin user: {email}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python scripts/create_admin.py <email> <password>")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    asyncio.run(create_admin(email, password))
