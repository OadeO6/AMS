# scripts/update_user_roles.py
import asyncio
import sys
import os
import uuid

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

from app.core.database import AsyncSessionFactory
from app.models.user import User, UserRole
from sqlalchemy import select

async def update_roles(email, roles):
    async with AsyncSessionFactory() as session:
        res = await session.execute(select(User).where(User.email == email))
        user = res.scalar_one_or_none()
        if not user:
            print(f"Error: User with email {email} not found.")
            return

        user.roles = roles
        await session.commit()
        print(f"Successfully updated roles for {email} to {roles}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/update_user_roles.py <email> <role1> <role2> ...")
        sys.exit(1)
    
    email = sys.argv[1]
    roles = sys.argv[2:]
    asyncio.run(update_roles(email, roles))
