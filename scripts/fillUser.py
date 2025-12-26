import asyncio
import httpx
import random
import string
import csv
from faker import Faker

API_URL = "https://db_api.trashcode.dev/api/users/"
TOTAL_USERS = 100
CONCURRENT_LIMIT = 5
fake = Faker()

def generate_user():
    pw = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(12))
    
    raw_phones = [fake.phone_number() for _ in range(random.randint(1, 3))]
    truncated_phones = [p[:20] for p in raw_phones] 

    return {
        "username": fake.bothify(text='user_##########')[:24],
        "email": fake.email(),
        "password": pw,
        "address": fake.address()[:256] if random.random() > 0.2 else None,
        "phones": truncated_phones if random.random() > 0.2 else None
    }

async def post_user(client, semaphore, user_index):
    payload = generate_user()
    async with semaphore:
        try:
            res = await client.post(API_URL, json=payload, timeout=10.0)
            
            if res.status_code in [200, 201]:
                return payload
            elif res.status_code in [301, 302, 307, 308]:
                return None
            else:
                print(f"[{user_index}] Failed: {res.status_code}")
                return None
        except Exception as e:
            return None

async def main():
    print(f"🚀 Starting high-speed data transmission of {TOTAL_USERS} records (Concurrency limit: {CONCURRENT_LIMIT})...")
    
    semaphore = asyncio.Semaphore(CONCURRENT_LIMIT)
    
    async with httpx.AsyncClient(verify=False, follow_redirects=False) as client:
        tasks = [post_user(client, semaphore, i) for i in range(TOTAL_USERS)]
        responses = await asyncio.gather(*tasks)
        results = [r for r in responses if r is not None]

    if results:
        fieldnames = ["username", "email", "password", "address", "phones"]
        with open('users.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        print("\n" + "="*30)
        print(f"Done! Successfully wrote: {len(results)} / {TOTAL_USERS} records")
        print("="*30)
    else:
        print("\n[Warning] Unable to write any data, please check API status or redirect address.")

if __name__ == "__main__":
    asyncio.run(main())