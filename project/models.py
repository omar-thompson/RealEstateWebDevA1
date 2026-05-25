"""
MODELS.PY (flask_mysqldb version)

IMPORTANT:
- This project does NOT use SQLAlchemy ORM
- These are ONLY STRUCTURE DEFINITIONS for reference
- All database operations are done in views.py using raw SQL
"""

# =========================
# USERS TABLE
# =========================
"""
Table: users

user_id        INT PRIMARY KEY AUTO_INCREMENT
full_name      VARCHAR(100)
email          VARCHAR(150) UNIQUE
phone_number   VARCHAR(20)
password_hash  VARCHAR(255)
prefers_pets boolean default FALSE,
prefers_social_lifestyle boolean default FALSE,
description    TEXT
role           ENUM('admin', 'seller', 'buyer')
created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
"""

# =========================
# PROPERTIES TABLE
# =========================
"""
Table: properties

property_id     INT PRIMARY KEY AUTO_INCREMENT
owner_id        INT (FK -> users.user_id)
address         VARCHAR(255)
suburb          VARCHAR(100)
state           VARCHAR(100)
bedrooms        INT
bathrooms       INT
pet_friendly    BOOLEAN
lifestyle_type  ENUM('quiet', 'social')
property_type   ENUM('house', 'apartment', 'unit', 'granny_flat')
image_url       VARCHAR(255)
created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
"""

# =========================
# LISTINGS TABLE
# =========================
"""
Table: listings

listing_id      INT PRIMARY KEY AUTO_INCREMENT
property_id     INT (FK -> properties.property_id)
title           VARCHAR(150)
description     TEXT
weekly_price    DECIMAL(10,2)
availability_status ENUM('available', 'pending', 'rented')
created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
"""

# =========================
# FAVOURITES TABLE
# =========================
"""
Table: favourites

favourite_id    INT PRIMARY KEY AUTO_INCREMENT
user_id         INT (FK -> users.user_id)
listing_id      INT (FK -> listings.listing_id)
date_saved      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
"""

# =========================
# ENQUIRIES TABLE
# =========================
"""
Table: enquiries

enquiry_id      INT PRIMARY KEY AUTO_INCREMENT
user_id         INT (FK -> users.user_id)
listing_id      INT (FK -> listings.listing_id)
message         TEXT
status          ENUM('new', 'responded', 'closed')
date_created    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
"""

# =========================
# REVIEWS TABLE
# =========================
"""
Table: reviews

review_id       INT PRIMARY KEY AUTO_INCREMENT
user_id         INT (FK -> users.user_id)
listing_id      INT (FK -> listings.listing_id)
rating          INT (1–5)
comment         TEXT
date_created    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
"""

# =========================
# DOCUMENTS TABLE
# =========================
"""
Table: documents

document_id     INT PRIMARY KEY AUTO_INCREMENT
listing_id      INT (FK -> listings.listing_id)
doc_type        VARCHAR(50)
doc_url         VARCHAR(255)
upload_date     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
"""

# =========================
# OFFERS TABLE
# =========================
"""
Table: offers

offer_id        INT PRIMARY KEY AUTO_INCREMENT
user_id         INT (FK -> users.user_id)
listing_id      INT (FK -> listings.listing_id)
offer_amount    DECIMAL(10,2)
status          ENUM('pending', 'accepted', 'rejected')
created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
"""


