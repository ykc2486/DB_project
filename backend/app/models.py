
CREATE_TABLE_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS users (
        user_id SERIAL PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE,
        email VARCHAR(100) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        address VARCHAR(255),
        is_active BOOLEAN DEFAULT TRUE,
        join_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE INDEX IF NOT EXISTS ix_users_username ON users (username);
    """,
    """
    CREATE INDEX IF NOT EXISTS ix_users_email ON users (email);
    """,
    """
    CREATE TABLE IF NOT EXISTS phones (
        phone_id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(user_id),
        phone_number VARCHAR(20) NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS categories (
        category_id SERIAL PRIMARY KEY,
        category_name VARCHAR(100) NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS items (
        item_id SERIAL PRIMARY KEY,
        title VARCHAR(100) NOT NULL,
        description TEXT,
        condition VARCHAR(50) NOT NULL,
        owner_id INTEGER NOT NULL REFERENCES users(user_id),
        post_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        price INTEGER,
        exchange_type BOOLEAN DEFAULT FALSE,
        status BOOLEAN DEFAULT TRUE,
        desired_item VARCHAR(100),
        category INTEGER NOT NULL REFERENCES categories(category_id),
        total_images INTEGER DEFAULT 0
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS item_images (
        image_id SERIAL PRIMARY KEY,
        item_id INTEGER NOT NULL REFERENCES items(item_id),
        image_data_name VARCHAR(255) NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS wishlist (
        wishlist_id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(user_id),
        item_id INTEGER NOT NULL REFERENCES items(item_id),
        added_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id SERIAL PRIMARY KEY,
        item_id INTEGER NOT NULL REFERENCES items(item_id),
        buyer_id INTEGER NOT NULL REFERENCES users(user_id),
        seller_id INTEGER NOT NULL REFERENCES users(user_id),
        transaction_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        status VARCHAR(50) DEFAULT 'pending',
        completion_date TIMESTAMP WITH TIME ZONE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS messages (
        message_id SERIAL PRIMARY KEY,
        sender_id INTEGER NOT NULL REFERENCES users(user_id),
        receiver_id INTEGER NOT NULL REFERENCES users(user_id),
        content TEXT NOT NULL,
        sent_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        is_read BOOLEAN DEFAULT FALSE,
        item_id INTEGER REFERENCES items(item_id)
    );
    """
]
