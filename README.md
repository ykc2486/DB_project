# Final Project - A C2C Second-hand Trading Platform Database

## 0. Team Infomation
| Name | Student ID | Department/Year |
| ---- | ---------- | --------------- |
| 邱元廣 | 113550025 | CS/117 | 
| 謝亞序 | 113550109 | CS/117 |
| 陳泓淯 | 113550015 | CS/117 |

## 1. Introduction
Our application, Second-Hand Item Trading & Exchange Platform, is a web-based C2C (Consumer-to-Consumer) marketplace designed to address the issue of resource waste and the high cost of new goods for students. The system allows users to list items for sale or exchange, manage personal wishlists, and communicate directly through an integrated messaging system. The core functions include secure user authentication, item listing with image uploads, robust search/filtering, and a structured transaction management system to ensure clear trade status tracking.

## 2. Design Motivation

- **Problem addressed:** 
Students often have useful items (textbooks, furniture) they no longer need, while others seek these items at lower prices. Existing social media groups lack structured searching, transaction history, and the needed in messaging.

- **Suitability:**
Our system provides a centralized database that stores items, tracks availability in real-time, and archives conversation history between specific buyers and sellers, making the process more efficient than unstructured platforms.

- **Need for a database:**
A database is essential to maintain data persistence (user accounts, item details), referential integrity (linking transactions to specific users and items), and concurrency control (preventing two users from buying the same item simultaneously).

## 3. Database Design

### users
| Column Name | Data Type | Constraints |
| :--- | :--- | :--- |
| user_id | SERIAL | PRIMARY KEY |
| username | VARCHAR(50) | NOT NULL, UNIQUE |
| email | VARCHAR(100) | NOT NULL, UNIQUE |
| password_hash | VARCHAR(255) | NOT NULL |
| address | VARCHAR(255) | |
| is_active | BOOLEAN | DEFAULT TRUE |
| join_date | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP |

### phones
| Column Name | Data Type | Constraints |
| :--- | :--- | :--- |
| phone_id | SERIAL | PRIMARY KEY |
| user_id | INTEGER | NOT NULL, REFERENCES users(user_id) |
| phone_number | VARCHAR(20) | NOT NULL |

### categories
| Column Name | Data Type | Constraints |
| :--- | :--- | :--- |
| category_id | SERIAL | PRIMARY KEY |
| category_name | VARCHAR(100) | NOT NULL |

### items
| Column Name | Data Type | Constraints |
| :--- | :--- | :--- |
| item_id | SERIAL | PRIMARY KEY |
| title | VARCHAR(100) | NOT NULL |
| description | TEXT | |
| condition | VARCHAR(50) | NOT NULL |
| owner_id | INTEGER | NOT NULL, REFERENCES users(user_id) |
| post_date | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP |
| price | INTEGER | |
| exchange_type | BOOLEAN | DEFAULT FALSE |
| status | BOOLEAN | DEFAULT TRUE |
| desired_item | VARCHAR(100) | |
| category | INTEGER | NOT NULL, REFERENCES categories(category_id) |
| total_images | INTEGER | DEFAULT 0 |

### item_images
| Column Name | Data Type | Constraints |
| :--- | :--- | :--- |
| image_id | SERIAL | PRIMARY KEY |
| item_id | INTEGER | NOT NULL, REFERENCES items(item_id) |
| image_data_name | VARCHAR(255) | NOT NULL |

### wishlist
| Column Name | Data Type | Constraints |
| :--- | :--- | :--- |
| wishlist_id | SERIAL | PRIMARY KEY |
| user_id | INTEGER | NOT NULL, REFERENCES users(user_id) |
| item_id | INTEGER | NOT NULL, REFERENCES items(item_id) |
| added_date | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP |

### transactions
| Column Name | Data Type | Constraints |
| :--- | :--- | :--- |
| transaction_id | SERIAL | PRIMARY KEY |
| item_id | INTEGER | NOT NULL, REFERENCES items(item_id) |
| buyer_id | INTEGER | NOT NULL, REFERENCES users(user_id) |
| seller_id | INTEGER | NOT NULL, REFERENCES users(user_id) |
| transaction_date | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP |
| status | VARCHAR(50) | DEFAULT 'pending' |
| completion_date | TIMESTAMP WITH TIME ZONE | |

### messages
| Column Name | Data Type | Constraints |
| :--- | :--- | :--- |
| message_id | SERIAL | PRIMARY KEY |
| sender_id | INTEGER | NOT NULL, REFERENCES users(user_id) |
| receiver_id | INTEGER | NOT NULL, REFERENCES users(user_id) |
| content | TEXT | NOT NULL |
| sent_at | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP |
| is_read | BOOLEAN | DEFAULT FALSE |
| item_id | INTEGER | REFERENCES items(item_id) |

