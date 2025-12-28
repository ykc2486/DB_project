<img width="2750" height="1373" alt="Gemini_Generated_Image_aq7ut0aq7ut0aq7u" src="https://github.com/user-attachments/assets/1ac93e1b-e7ec-4203-8068-52f5d8958541" /># Final Project - A C2C Second-hand Trading Platform Database

Our code base repository: **https://github.com/ykc2486/DB_project/**

Our frontend: **https://db.trashcode.dev/**

## 0. Team Information
### Team 2
| Name | Student ID | Department/Year |
| ---- | ---------- | --------------- |
| 邱元廣 | 113550025 | CS/117 | 
| 謝亞序 | 113550109 | CS/117 |
| 陳泓淯 | 113550015 | CS/117 |

## 1. Introduction
Our application is a web-based C2C (Consumer-to-Consumer) marketplace designed to address the issue of resource waste and the high cost of new goods for students. The system allows users to list items for sale or exchange, manage personal wishlists, and communicate directly through an integrated messaging system. The core functions include secure user authentication, item listing with image uploads, robust search/filtering, and a structured transaction management system to ensure clear trade status tracking.

## 2. Design Motivation

- **Problem addressed:** 
Students often have useful items (textbooks, furniture) they no longer need, while others seek these items at lower prices. Existing social media groups lack structured searching, transaction history, and the needed in messaging.

- **Suitability:**
Our system provides a centralized database that stores items, tracks availability in real-time, and archives conversation history between specific buyers and sellers, making the process more efficient than unstructured platforms.

- **Need for a database:**
A database is essential to maintain data persistence (user accounts, item details), referential integrity (linking transactions to specific users and items), and concurrency control (preventing two users from buying the same item simultaneously).

## 3. Database Design

### 3.1 Final Database Schema

#### users
| Column Name | Data Type | Constraints |
| :--- | :--- | :--- |
| user_id | SERIAL | PRIMARY KEY |
| username | VARCHAR(50) | NOT NULL, UNIQUE |
| email | VARCHAR(100) | NOT NULL, UNIQUE |
| password_hash | VARCHAR(255) | NOT NULL |
| address | VARCHAR(255) | |
| is_active | BOOLEAN | DEFAULT TRUE |
| join_date | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP |

#### phones
| Column Name | Data Type | Constraints |
| :--- | :--- | :--- |
| phone_id | SERIAL | PRIMARY KEY |
| user_id | INTEGER | NOT NULL, REFERENCES users(user_id), INDEX |
| phone_number | VARCHAR(20) | NOT NULL |

#### items
| Column Name | Data Type | Constraints |
| :--- | :--- | :--- |
| item_id | SERIAL | PRIMARY KEY |
| title | VARCHAR(100) | NOT NULL |
| description | TEXT | |
| condition | VARCHAR(50) | NOT NULL |
| owner_id | INTEGER | NOT NULL, REFERENCES users(user_id), INDEX |
| post_date | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP, INDEX |
| price | INTEGER | INDEX |
| exchange_type | BOOLEAN | DEFAULT FALSE |
| status | BOOLEAN | DEFAULT TRUE |
| desired_item | VARCHAR(100) | |
| category | INTEGER | NOT NULL, REFERENCES categories(category_id), INDEX |
| total_images | INTEGER | DEFAULT 0 |

#### item_images
| Column Name | Data Type | Constraints |
| :--- | :--- | :--- |
| image_id | SERIAL | PRIMARY KEY |
| item_id | INTEGER | NOT NULL, REFERENCES items(item_id), INDEX |
| image_data_name | VARCHAR(255) | NOT NULL |

#### wishlist
| Column Name | Data Type | Constraints |
| :--- | :--- | :--- |
| wishlist_id | SERIAL | PRIMARY KEY |
| user_id | INTEGER | NOT NULL, REFERENCES users(user_id), INDEX |
| item_id | INTEGER | NOT NULL, REFERENCES items(item_id), INDEX |
| added_date | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP |

#### transactions
| Column Name | Data Type | Constraints |
| :--- | :--- | :--- |
| transaction_id | SERIAL | PRIMARY KEY |
| item_id | INTEGER | NOT NULL, REFERENCES items(item_id), INDEX |
| buyer_id | INTEGER | NOT NULL, REFERENCES users(user_id), INDEX |
| seller_id | INTEGER | NOT NULL, REFERENCES users(user_id), INDEX |
| transaction_date | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP, INDEX |
| status | VARCHAR(50) | DEFAULT 'pending' |
| completion_date | TIMESTAMP WITH TIME ZONE | |

#### messages
| Column Name | Data Type | Constraints |
| :--- | :--- | :--- |
| message_id | SERIAL | PRIMARY KEY |
| sender_id | INTEGER | NOT NULL, REFERENCES users(user_id), INDEX |
| receiver_id | INTEGER | NOT NULL, REFERENCES users(user_id), INDEX |
| content | TEXT | NOT NULL |
| sent_at | TIMESTAMP WITH TIME ZONE | DEFAULT CURRENT_TIMESTAMP, INDEX |
| is_read | BOOLEAN | DEFAULT FALSE |
| item_id | INTEGER | REFERENCES items(item_id), INDEX |

#### Schema Changes from Milestone 2:

##### 1. Categories Table

**Table:** `categories`

**Change Type:** Removed

**Specific Change:** Removed the `categories` table entirely.

**Rationale:** We decided to simplify the category management. Instead of a separate table, we decided to handle categories within the application logic to reduce join complexity and maintenance overhead.

##### 2. Reviews Table

**Table:** `reviews`

**Change Type:** Removed

**Specific Change:** Removed the `reviews` table entirely.

**Rationale:** The review and rating feature was removed from the scope of this version of the project to focus on core transaction and messaging functionalities.

##### 3. Users Table

**Table:** `users`

**Change Type:** Modified

**Specific Change:** Removed `average_rating` column.

**Rationale:** Since the `reviews` table and the review feature were removed, the `average_rating` column in the `users` table became redundant.

##### 4. Item Images Table

**Table:** `item_images`

**Change Type:** Modified

**Specific Change:** Changed `image_data` column to `image_data_name`.

**Rationale:** We changed the `image_data` column to `image_data_name` to store the image file names instead of binary data. This change improves database performance and scalability by offloading image storage to a dedicated file storage system or CDN, reducing database size and improving query performance.

### 3.2 Keys and Index Design Rationale

We have carefully selected primary keys, foreign keys, and indexes to ensure data integrity and optimize query performance based on our application's specific access patterns.

#### 3.2.1 Primary Keys
Every table in our schema (`users`, `phones`, `items`, `item_images`, `wishlist`, `transactions`, `messages`) utilizes a `SERIAL` column as a **Primary Key** (e.g., `user_id`, `item_id`).
*   **Reason:** This provides a unique, non-null identifier for every record, ensuring **Entity Integrity**. It allows for O(1) lookup performance when retrieving a specific record and serves as a stable reference point for relationships with other tables.

#### 3.2.2 Foreign Keys
We extensively use **Foreign Keys** to link related data.
*   **Columns:** `items.owner_id`, `items.category`, `phones.user_id`, `transactions.buyer_id`, `transactions.seller_id`, `messages.sender_id`, etc.
*   **Reason:** These keys enforce **Referential Integrity**. They ensure that an item cannot exist without a valid owner, and a transaction must reference valid users. This prevents data inconsistency and orphaned records.

#### 3.2.3 Indexes
We added indexes to specific columns to optimize query performance. Here is the breakdown of why they are helpful (or why some were omitted):

**1. Foreign Key Indexes (Helpful)**
*   **Columns:** `owner_id`, `category`, `item_id`, `user_id`, `buyer_id`, `seller_id`, `sender_id`, `receiver_id`.
*   **Rationale:** These columns are frequently used in `JOIN` conditions and `WHERE` clauses (e.g., "Find all items sold by User X"). Without indexes, the database would perform full table scans for these common lookups. Indexing them significantly speeds up join operations and relationship traversals.

**2. Sorting and Range Query Indexes (Helpful)**
*   **Columns:** `price`, `post_date`, `transaction_date`, `sent_at`.
*   **Rationale:** Our application features sorting items by price and displaying feeds chronologically. Indexes on these columns allow the database to retrieve sorted results efficiently (avoiding expensive sort operations) and quickly filter ranges (e.g., "Items posted in the last week").

**3. Unique Indexes (Helpful)**
*   **Columns:** `username`, `email`.
*   **Rationale:** These are enforced by `UNIQUE` constraints, which automatically create indexes. They are crucial for fast lookups during user login and registration to check for duplicates.

**4. Low Cardinality Columns (Index Omitted/Not Helpful)**
*   **Columns:** `status`, `exchange_type`, `is_read`.
*   **Rationale:** We decided **not** to index these boolean/low-cardinality columns individually. Since they only have a few unique values (True/False), an index would likely not be selective enough to be used by the query planner (a full table scan is often faster for fetching a large portion of the table).

### 3.3 Design Justification: Normalization and Performance

We have chosen to analyze our database design through the lens of **Normalization (BCNF)** and its trade-offs with performance.

#### BCNF Compliance
Our database schema is largely designed to adhere to **Boyce-Codd Normal Form (BCNF)**.

-   **Multi-valued Attributes**: We handled multi-valued attributes like phone numbers and images by creating separate tables (`phones`, `item_images`) linked by foreign keys, rather than storing them as delimited strings or arrays, satisfying First Normal Form (1NF) and enabling proper indexing and querying.

#### Performance Trade-offs and Denormalization
While strict normalization eliminates redundancy, we introduced a deliberate **denormalization** in the `items` table for performance reasons:

-   **The `total_images` Attribute**: The `items` table contains a `total_images` column. Strictly speaking, this is a derived attribute dependent on the count of related rows in the `item_images` table. Storing this violates BCNF because it introduces redundancy; the information is already available by querying `item_images`.
-   **Justification**: This trade-off was made to optimize the **Read** performance of the item feed. The "browse items" page is the most frequently accessed part of the application. By storing `total_images`, we can display the number of images on the product card (e.g., "iPhone 13 (5 images)") using a simple `SELECT` from the `items` table, avoiding a costly `JOIN` and `GROUP BY/COUNT` operation on the `item_images` table for every single item in the list. This significantly reduces the database load for read-heavy workloads, which is a standard practice discussed in performance tuning lectures when the cost of maintaining consistency (updating `total_images` on insert/delete) is outweighed by the read efficiency.

## 4. Data Sources

### 4.1 Data Source and Original Format
Because there is no publicly available dataset that fits our specific schema and requirements, we generated synthetic data using **Python scripts**. These scripts create user profiles, item listings, categories, transactions, and messages to populate our database for testing and demonstration purposes. The data generation process ensures that the relationships between entities are maintained according to our database design.

### 4.2 Data Output
Below are the query result displaying 105 rows of data in the item table in our database using the following command.

```bash
sudo docker exec -it my_postgres_db psql -U charlieKirk -d mydb -c "COPY (SELECT  item_id, title, condition, owner_id, post_date, price, exchange_type, status, desired_item, category, total_images FROM items) TO STDOUT WITH (FORMAT CSV, HEADER, ENCODING 'UTF8')" > output.csv
```

```csv
item_id,title,condition,owner_id,post_date,price,exchange_type,status,desired_item,category,total_images
2,滑鼠,良好,2,2025-12-24 13:20:46.293118+00,670,f,f,,1,1
15,Synergized well-modulated knowledge user,全新,349,2025-12-27 05:14:04.691739+00,2683,f,f,"",5,0
1,茶裏王,損壞,1,2025-12-24 13:03:33.675106+00,67,f,f,"",1,1
4,可愛的狗勾,良好,3,2025-12-24 15:04:24.013634+00,0,t,t,卯咪,1,1
5,Focused foreground protocol,良好,348,2025-12-27 05:14:04.365595+00,1789,f,t,"",4,0
6,Distributed explicit installation,全新,347,2025-12-27 05:14:04.339904+00,6177,f,t,"",4,0
7,Enterprise-wide zero tolerance circuit,損壞,354,2025-12-27 05:14:04.394678+00,0,t,t,價格,3,0
10,Switchable attitude-oriented matrix,全新,359,2025-12-27 05:14:04.590058+00,7934,f,t,"",2,0
12,Virtual radical neural-net,全新,358,2025-12-27 05:14:04.603067+00,0,t,t,更新,1,0
14,Synergistic 6thgeneration protocol,全新,357,2025-12-27 05:14:04.685012+00,1835,f,t,"",4,0
16,Optimized asynchronous functionalities,良好,361,2025-12-27 05:14:04.687636+00,0,t,f,出來,4,0
13,Multi-lateral 24/7 project,全新,350,2025-12-27 05:14:04.620128+00,6841,f,f,"",5,0
9,Polarized interactive groupware,全新,356,2025-12-27 05:14:04.586222+00,7562,f,f,"",2,0
8,Intuitive encompassing matrix,損壞,353,2025-12-27 05:14:04.403624+00,197,f,f,"",2,0
17,Sharable discrete circuit,普通,364,2025-12-27 05:14:04.710261+00,2136,f,t,"",5,0
22,Integrated responsive database,良好,349,2025-12-27 05:14:04.801372+00,4854,f,t,"",4,0
30,Multi-channeled empowering capacity,損壞,354,2025-12-27 05:14:04.972556+00,6008,f,t,"",5,0
49,Organized full-range leverage,全新,354,2025-12-27 05:14:05.351966+00,3894,f,t,"",4,0
55,Multi-tiered executive toolset,普通,362,2025-12-27 05:14:05.452507+00,0,t,t,問題,1,0
64,Upgradable tangible migration,全新,351,2025-12-27 05:14:05.650488+00,4736,f,t,"",3,0
180,Enhanced bandwidth-monitored moderator,損壞,160,2025-12-27 05:18:39.140719+00,0,t,t,如何,1,0
39,Pre-emptive cohesive emulation,普通,347,2025-12-27 05:14:05.168649+00,6370,f,f,"",5,0
71,Customer-focused impactful hardware,普通,360,2025-12-27 05:14:05.758955+00,5369,f,f,"",3,0
34,Front-line intangible data-warehouse,普通,347,2025-12-27 05:14:05.073883+00,950,f,f,"",5,0
25,Proactive logistical analyzer,全新,353,2025-12-27 05:14:04.890064+00,0,t,f,他們,4,0
18,Vision-oriented solution-oriented array,普通,355,2025-12-27 05:14:04.708265+00,0,t,t,研究,4,0
23,Focused human-resource solution,全新,363,2025-12-27 05:14:04.806052+00,5640,f,t,"",1,0
27,Quality-focused value-added projection,損壞,352,2025-12-27 05:14:04.892989+00,9947,f,t,"",2,0
31,Open-source radical challenge,損壞,348,2025-12-27 05:14:04.983742+00,0,t,t,覺得,4,0
35,Switchable bi-directional extranet,普通,346,2025-12-27 05:14:05.075977+00,800,f,t,"",4,0
40,Automated secondary analyzer,全新,357,2025-12-27 05:14:05.170613+00,6541,f,t,"",1,0
50,Expanded fresh-thinking time-frame,全新,363,2025-12-27 05:14:05.353771+00,9793,f,t,"",4,0
65,Persevering background array,損壞,348,2025-12-27 05:14:05.651371+00,531,f,t,"",5,0
70,Visionary holistic initiative,良好,364,2025-12-27 05:14:05.749566+00,4087,f,t,"",5,0
75,Up-sized fault-tolerant toolset,損壞,358,2025-12-27 05:14:05.850388+00,7962,f,t,"",1,0
60,Open-architected executive policy,普通,363,2025-12-27 05:14:05.551376+00,7927,f,f,"",1,0
45,Monitored context-sensitive secured line,普通,347,2025-12-27 05:14:05.271432+00,0,t,f,今天,4,0
19,Future-proofed value-added middleware,全新,352,2025-12-27 05:14:04.779715+00,0,t,t,法律,3,0
24,Synchronized 4thgeneration emulation,損壞,348,2025-12-27 05:14:04.876317+00,0,t,t,幫助,2,0
29,Programmable homogeneous Graphical User Interface,損壞,366,2025-12-27 05:14:04.97052+00,8150,f,t,"",4,0
36,Function-based multimedia groupware,全新,349,2025-12-27 05:14:05.066093+00,643,f,t,"",2,0
41,Fundamental neutral knowledge user,全新,351,2025-12-27 05:14:05.173015+00,8539,f,t,"",3,0
46,Organic intermediate project,損壞,360,2025-12-27 05:14:05.26863+00,0,t,t,推薦,5,0
51,Business-focused explicit encryption,普通,356,2025-12-27 05:14:05.372722+00,229,f,t,"",2,0
67,Upgradable methodical Graphical User Interface,損壞,354,2025-12-27 05:14:05.667774+00,0,t,t,網絡,1,0
77,Digitized analyzing website,損壞,356,2025-12-27 05:14:05.861268+00,9761,f,t,"",4,0
63,Focused tertiary knowledge user,全新,356,2025-12-27 05:14:05.570671+00,6972,f,f,"",4,0
58,Polarized logistical service-desk,損壞,356,2025-12-27 05:14:05.467294+00,3407,f,f,"",1,0
20,Public-key reciprocal interface,全新,364,2025-12-27 05:14:04.792705+00,0,t,t,目前,4,0
26,Open-source next generation installation,全新,356,2025-12-27 05:14:04.887675+00,0,t,t,以后,2,0
37,Vision-oriented 24/7 open system,良好,366,2025-12-27 05:14:05.07892+00,3305,f,t,"",1,0
48,Profound stable budgetary management,普通,354,2025-12-27 05:14:05.287497+00,0,t,t,孩子,4,0
53,Team-oriented composite open system,良好,357,2025-12-27 05:14:05.374571+00,5981,f,t,"",2,0
62,Extended motivating process improvement,普通,346,2025-12-27 05:14:05.568598+00,0,t,t,以后,2,0
66,Quality-focused object-oriented workforce,良好,352,2025-12-27 05:14:05.654811+00,0,t,t,不要,2,0
74,Automated grid-enabled Internet solution,全新,358,2025-12-27 05:14:05.838636+00,3215,f,t,"",4,0
79,Switchable tertiary archive,全新,364,2025-12-27 05:14:05.933909+00,5935,f,t,"",1,0
42,Automated 24hour initiative,良好,359,2025-12-27 05:14:05.1733+00,8820,f,f,"",3,0
57,Open-source neutral archive,全新,349,2025-12-27 05:14:05.47043+00,0,t,f,的人,5,0
33,Devolved methodical moratorium,普通,366,2025-12-27 05:14:04.991226+00,0,t,f,隻有,2,0
43,Virtual 5thgeneration matrix,良好,356,2025-12-27 05:14:05.179368+00,3808,f,t,"",1,0
52,Future-proofed discrete framework,損壞,348,2025-12-27 05:14:05.370747+00,1071,f,t,"",4,0
78,Digitized next generation architecture,損壞,366,2025-12-27 05:14:05.85953+00,0,t,t,的人,5,0
82,Cross-group heuristic contingency,良好,358,2025-12-27 05:14:05.964178+00,2022,f,f,"",1,0
28,Fully-configurable national methodology,普通,349,2025-12-27 05:14:04.887975+00,2757,f,f,"",5,0
68,Centralized client-driven success,良好,355,2025-12-27 05:14:05.671441+00,1907,f,f,"",5,0
47,Virtual secondary complexity,良好,359,2025-12-27 05:14:05.272943+00,1457,f,f,"",1,0
38,Seamless directional moderator,良好,354,2025-12-27 05:14:05.09378+00,5547,f,f,"",2,0
21,Implemented intangible help-desk,損壞,348,2025-12-27 05:14:04.790753+00,3486,f,f,"",4,0
32,Synergized upward-trending process improvement,普通,346,2025-12-27 05:14:04.988676+00,0,t,f,學生,3,0
72,Vision-oriented clear-thinking access,全新,355,2025-12-27 05:14:05.764346+00,0,t,f,詳細,4,0
91,Profit-focused exuding groupware,全新,361,2025-12-27 05:14:06.149448+00,3790,f,t,"",4,0
96,Vision-oriented bi-directional workforce,良好,351,2025-12-27 05:14:06.245848+00,3389,f,t,"",1,0
100,Networked maximized focus group,良好,350,2025-12-27 05:14:06.333715+00,3019,f,t,"",3,0
76,Optimized web-enabled throughput,普通,355,2025-12-27 05:14:05.857985+00,4819,f,f,"",1,0
81,Operative national emulation,普通,359,2025-12-27 05:14:05.95014+00,0,t,f,工程,4,0
86,Inverse client-driven capability,普通,351,2025-12-27 05:14:06.051214+00,5905,f,f,"",2,0
80,Total transitional neural-net,全新,358,2025-12-27 05:14:05.942885+00,1045,f,t,"",4,0
94,Organized zero-defect array,全新,364,2025-12-27 05:14:06.229841+00,0,t,t,專業,5,0
85,Cloned dynamic parallelism,普通,363,2025-12-27 05:14:06.043016+00,2298,f,f,"",5,0
99,Monitored client-driven framework,良好,351,2025-12-27 05:14:06.317145+00,9957,f,f,"",3,0
89,Extended uniform algorithm,損壞,359,2025-12-27 05:14:06.137041+00,4468,f,f,"",1,0
88,User-friendly asynchronous matrices,全新,353,2025-12-27 05:14:06.067607+00,0,t,t,什麼,1,0
93,Optimized executive encryption,全新,363,2025-12-27 05:14:06.172257+00,0,t,t,完成,2,0
83,Reactive heuristic application,損壞,360,2025-12-27 05:14:05.970106+00,0,t,f,他的,2,0
98,Expanded 24/7 Graphical User Interface,損壞,348,2025-12-27 05:14:06.260628+00,4540,f,f,"",3,0
90,Digitized zero tolerance groupware,損壞,352,2025-12-27 05:14:06.135398+00,8671,f,t,"",2,0
95,Team-oriented maximized initiative,普通,347,2025-12-27 05:14:06.242681+00,0,t,t,不斷,1,0
101,Horizontal 5thgeneration circuit,損壞,348,2025-12-27 05:14:06.34131+00,5359,f,t,"",4,0
84,Team-oriented systemic algorithm,損壞,351,2025-12-27 05:14:06.034725+00,0,t,f,如此,5,0
87,Managed demand-driven help-desk,損壞,359,2025-12-27 05:14:06.055103+00,0,t,t,完成,5,0
97,Devolved homogeneous emulation,良好,351,2025-12-27 05:14:06.256861+00,0,t,t,美國,2,0
103,Networked 3rdgeneration installation,良好,159,2025-12-27 05:18:37.117746+00,8346,f,t,"",2,0
105,Innovative executive focus group,良好,168,2025-12-27 05:18:37.19405+00,8571,f,t,"",4,0
106,Profound bifurcated database,良好,157,2025-12-27 05:18:37.195694+00,8062,f,t,"",5,0
107,Phased asymmetric software,良好,158,2025-12-27 05:18:37.247893+00,5276,f,t,"",2,0
108,Ergonomic 4thgeneration encryption,良好,173,2025-12-27 05:18:37.249815+00,2386,f,t,"",5,0
111,Virtual transitional groupware,全新,155,2025-12-27 05:18:37.351953+00,9448,f,t,"",2,0
109,Synchronized foreground policy,全新,164,2025-12-27 05:18:37.297492+00,2345,f,f,"",1,0
104,Centralized bandwidth-monitored access,良好,160,2025-12-27 05:18:37.116104+00,7498,f,f,"",2,0
102,Down-sized system-worthy conglomeration,良好,363,2025-12-27 05:14:06.343823+00,5497,f,f,"",4,0
110,Managed encompassing success,普通,174,2025-12-27 05:18:37.30281+00,3607,f,f,"",1,0
112,Horizontal bifurcated benchmark,普通,148,2025-12-27 05:18:37.357833+00,5625,f,t,"",3,0
122,Up-sized explicit hub,全新,164,2025-12-27 05:18:37.615987+00,1052,f,t,"",5,0
```



### 4.3 Challenges in Data Collection and Overcoming Strategies

1. **Maintaining Logical Consistency and Referential Integrity**

    **Challenge:** The biggest challenge in generating synthetic data was ensuring that relationships between entities remained logically consistent. For instance, a transaction record could not exist without referencing a valid user_id for both a buyer and a seller, and an item_id that was actually available.

    **Resolution:** We developed a "dependency-aware" script that followed a strict execution order: first creating users and categories, then items, and finally transactions, wishlists, and messages. This ensured that all foreign key constraints were satisfied before dependent data was inserted.

2. **Simulating Realistic User Behavior with Synthetic Data**

    **Challenge:** It was difficult to make the data look "real" rather than random noise. Simply generating random strings for item titles or descriptions made the marketplace look disorganized and non-functional.

    **Resolution:** We utilized the Python Faker library to generate localized usernames and valid email formats. To make item listings realistic, we combined Faker's text generation with predefined lists of university-related goods (e.g., "Calculus Textbook," "Office Chair") and used weighted randomizers to assign prices based on the item's condition.

3. **Validating Backend Logic During Population**

    **Challenge:** Directly injecting data into the database using SQL scripts bypasses the application's business logic, such as password hashing or image file management. This could lead to a database full of "dead" data that doesn't work with the actual frontend.

    **Resolution:** Instead of direct SQL injection, we programmed our data generation script to programmatically "hit" our REST API endpoints. By sending POST requests to `/users/` and `/items/`, we ensured that every generated user had a secure password hashed by Argon2 and every item listing went through our image-saving logic in routes.py, resulting in a fully functional and secure dataset.

## 5. Data sources to database

### 5.1 Database Creation Process
Our system "CREATES" the database using a programmatic infrastructure-as-code approach defined in `models.py`.

*   **Schema Initialization:** The system utilizes a list of `CREATE TABLE IF NOT EXISTS` SQL statements to build the database structure from scratch.
*   **Constraint Enforcement:** During creation, the system establishes `SERIAL PRIMARY KEY`s for unique identification, `FOREIGN KEY` references (such as `owner_id` in items referencing `user_id`) to ensure referential integrity, and `UNIQUE` constraints on sensitive fields like `username` and `email`.
*   **Indexing for Performance:** Immediately after table creation, the system executes commands to create indexes (e.g., `ix_users_username` and `ix_users_email`) to optimize search and login performance.

### 5.2 Methods of Importing Original Data
To populate the database with over 100 realistic tuples for testing and demonstration, we implemented a sophisticated automated import strategy:

*   **API-Driven Seeding:** Instead of using manual SQL scripts, we developed a Python script that uses the `Faker` library to generate realistic synthetic data. This script "hits" our actual REST API endpoints (e.g., `POST /users/` and `POST /items/`) to import data.
*   **Business Logic Validation:** By importing data through the API, we ensure that all synthetic data passes through our backend business logic, such as password hashing via `PasswordHasher` and category verification.
*   **Image File Management:** For item listings, the import process handles binary data by saving uploaded files to a local `./uploads` directory with unique UUID filenames and storing the corresponding path in the `item_images` table.

### 5.3 Strategies for Updating Data
As a dynamic marketplace, our system requires frequent updates to reflect real-time activity:

*   **Transactional State Updates:** When a trade is completed, the system triggers a raw SQL `UPDATE` to change the status of an item to `false`, effectively removing it from the public marketplace view.
*   **User-Initiated Modifications:** Users can update their item listings or transaction statuses through `PUT` requests, which execute parameterized raw SQL strings to ensure the database is updated securely and accurately.
*   **Referential Cleanup:** To maintain a clean database, the system includes deletion logic where removing an item also triggers a `DELETE` query for all associated records in the `item_images` table, preventing orphaned data.

## 6. Application with Database

### 6.1 Target Users & Design Customization
The primary target users are **University Students** who want to trade second-hand items. The system is designed to support a dual-role model where every user can act as both a buyer and a seller seamlessly.

*   **Buyers**:
    *   **Needs**: Efficiently find specific items (textbooks, electronics) at low prices and ensure the seller is responsive.
    *   **Design Customization**: We implemented a **Search and Filter Bar** (by keyword, price, category) on the main page to facilitate quick discovery. A **Wishlist** view allows buyers to track items they are interested in.
*   **Sellers**:
    *   **Needs**: Easily list items and manage incoming purchase requests.
    *   **Design Customization**: An **Upload Interface** simplifies the listing process. The **Transaction Dashboard** distinguishes between "Sales" (where the user is the seller) and "Purchases" (where the user is the buyer), allowing sellers to manage order status (e.g., marking a transaction as completed).

### 6.2 Functionalities
1.  **User Authentication**: Register, Login, and Profile Management (update address, phone).
2.  **Marketplace**: Browse items, Search by keyword, Filter by category, Sort by price/date.
3.  **Item Management**: Post new items with images, Edit item details, Delete items.
4.  **Transaction System**: Initiate purchase requests, View transaction history, Update transaction status (Pending -> Completed).
5.  **Messaging**: Send and receive messages related to specific items/transactions.
6.  **Wishlist**: Add/Remove items from a personal wishlist.

### 6.3 SQL Queries
Our application uses **Raw SQL** via SQLAlchemy's `text()` construct for all database operations. Below are the key queries used:

#### User Management
*   **Create User**:
    ```sql
    -- Insert core user data
    INSERT INTO users (username, email, password_hash, address, is_active, join_date)
    VALUES (:username, :email, :password_hash, :address, true, now())
    RETURNING user_id
    ```
*   **Get User Profile**:
    ```sql
    -- Fetch basic info
    SELECT * FROM users WHERE user_id = :user_id
    ```
*   **Update User**:
    ```sql
    -- Update core attributes
    UPDATE users SET email = :email WHERE user_id = :id
    UPDATE users SET address = :address WHERE user_id = :id
    ```

#### Item Operations
*   **List Items (with Search & Sort)**:
    ```sql
    -- Market feed with dynamic filtering and ordering
    SELECT * FROM items WHERE status = true 
    AND (title LIKE :search OR description LIKE :search)
    ORDER BY price ASC  -- or DESC, or post_date
    ```
*   **Create Item**:
    ```sql
    -- Insert item and record its post_date
    INSERT INTO items (title, description, condition, owner_id, price, exchange_type, status, desired_item, category, total_images, post_date)
    VALUES (:title, :description, :condition, :owner_id, :price, :exchange_type, true, :desired_item, :category, :total_images, now())
    RETURNING item_id, post_date
    ```
*   **Update Item**:
    ```sql
    UPDATE items 
    SET title = :title, description = :description, condition = :condition, 
        price = :price, exchange_type = :exchange_type, desired_item = :desired_item
    WHERE item_id = :item_id
    ```
*   **Delete Item**:
    ```sql
    DELETE FROM item_images WHERE item_id = :item_id;
    DELETE FROM items WHERE item_id = :item_id;
    ```

#### Transactions
*   **Create Transaction**:
    ```sql
    INSERT INTO transactions (item_id, buyer_id, seller_id, transaction_date, status)
    VALUES (:item_id, :buyer_id, :seller_id, now(), 'pending')
    RETURNING transaction_id, transaction_date
    ```
*   **Get User Transactions**:
    ```sql
    SELECT * FROM transactions 
    WHERE buyer_id = :user_id OR seller_id = :user_id
    ORDER BY transaction_date DESC
    ```
*   **Update Transaction Status**:
    ```sql
    UPDATE transactions 
    SET status = :status, completion_date = :cdate
    WHERE transaction_id = :tid
    RETURNING *
    ```

#### Messaging
*   **Get Conversation List**:
    ```sql
    -- Fetch unique chat partners with their latest item context
    SELECT DISTINCT ON (u.user_id)
        u.user_id, u.username, 
        i.item_id, i.title as item_title,
        img.image_data_name as item_image
    FROM users u
    JOIN messages m ON (u.user_id = m.sender_id OR u.user_id = m.receiver_id)
    LEFT JOIN items i ON m.item_id = i.item_id
    LEFT JOIN item_images img ON i.item_id = img.item_id
    WHERE (m.sender_id = :user_id OR m.receiver_id = :user_id)
      AND u.user_id != :user_id
    ```

### 6.4 Database Connection
The application connects to the database using **FastAPI** and **SQLAlchemy**.

1.  **Connection Engine**: We use `sqlalchemy.create_engine` to establish a connection pool to the PostgreSQL database. The connection string is constructed from environment variables (User, Password, DB Name).
2.  **Session Management**: We implemented a `get_db()` dependency function that yields a database session (`SessionLocal`) for each HTTP request. This ensures that each request has its own isolated transaction scope and the connection is properly closed after the request is processed.
3.  **Execution**: Although we use SQLAlchemy for connection management, we strictly use `db.execute(text("SQL..."))` to run the raw SQL queries listed above, bypassing the ORM layer to demonstrate direct SQL usage.

### 6.5 Deployment
We deployed our frontend Svelte application on **Cloudflare Pages**, accessible at `db.trashcode.dev`. The backend is hosted on a **Raspberry Pi** located in a dormitory. To expose the backend to the public internet and bypass NAT restrictions, we utilized **Cloudflare Tunnel**, making the API accessible at `db_api.trashcode.dev`. We chose to use distinct subdomains for the frontend and backend instead of path-based routing to fully leverage **Cloudflare's CDN** capabilities for improved load times and performance.

<img width="2750" height="1373" alt="Gemini_Generated_Image_aq7ut0aq7ut0aq7u" src="https://github.com/user-attachments/assets/cf53c5e3-e4a0-48f1-83e2-9dfe699e918a" />
