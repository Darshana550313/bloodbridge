from utils.db import execute, fetch_all, fetch_one


def find_user_by_email(email):
    return fetch_one("SELECT * FROM users WHERE email = %s", (email,))


def find_user_by_id(user_id):
    return fetch_one("SELECT * FROM users WHERE id = %s", (user_id,))


def create_user(name, email, password_hash, role):
    return execute(
        "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
        (name, email, password_hash, role),
    )


def upsert_donor(user_id, blood_group, city, phone, last_donation_date, eligibility_status):
    existing = fetch_one("SELECT donor_id FROM donors WHERE user_id = %s", (user_id,))
    if existing:
        execute(
            """
            UPDATE donors
            SET blood_group = %s, city = %s, phone = %s, last_donation_date = %s,
                eligibility_status = %s
            WHERE user_id = %s
            """,
            (blood_group, city, phone, last_donation_date, eligibility_status, user_id),
        )
        return existing["donor_id"]

    return execute(
        """
        INSERT INTO donors (user_id, blood_group, city, phone, last_donation_date, eligibility_status)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (user_id, blood_group, city, phone, last_donation_date, eligibility_status),
    )


def get_donor_by_user(user_id):
    return fetch_one(
        """
        SELECT d.*, u.name, u.email
        FROM donors d
        JOIN users u ON u.id = d.user_id
        WHERE d.user_id = %s
        """,
        (user_id,),
    )


def get_matching_requests(blood_group, city, donor_id=None):
    return fetch_all(
        """
        SELECT br.*, h.hospital_name, h.user_id AS hospital_user_id,
               dr.response_id, dr.response_status, dr.preferred_date, dr.units AS response_units
        FROM blood_requests br
        JOIN hospitals h ON h.hospital_id = br.hospital_id
        LEFT JOIN donation_responses dr
          ON dr.request_id = br.request_id AND dr.donor_id = %s
        WHERE br.blood_group = %s
          AND br.city = %s
          AND br.request_status IN ('Open', 'In Progress')
        ORDER BY FIELD(br.urgency, 'Critical', 'High', 'Medium', 'Low'), br.created_at DESC
        """,
        (donor_id or 0, blood_group, city),
    )


def create_donation(donor_id, donation_date, blood_group, units):
    return execute(
        """
        INSERT INTO donations (donor_id, donation_date, blood_group, units)
        VALUES (%s, %s, %s, %s)
        """,
        (donor_id, donation_date, blood_group, units),
    )


def create_donation_response(request_id, donor_id, message, preferred_date, units):
    return execute(
        """
        INSERT INTO donation_responses (request_id, donor_id, message, preferred_date, units, response_status)
        VALUES (%s, %s, %s, %s, %s, 'Pending')
        ON DUPLICATE KEY UPDATE
            message = VALUES(message),
            preferred_date = VALUES(preferred_date),
            units = VALUES(units),
            response_status = IF(response_status = 'Rejected', 'Pending', response_status),
            updated_at = CURRENT_TIMESTAMP
        """,
        (request_id, donor_id, message, preferred_date, units),
    )


def get_response_for_donor(request_id, donor_id):
    return fetch_one(
        "SELECT * FROM donation_responses WHERE request_id = %s AND donor_id = %s",
        (request_id, donor_id),
    )


def get_responses_for_donor(donor_id):
    return fetch_all(
        """
        SELECT dr.*, br.blood_group, br.quantity, br.urgency, br.city, br.request_status,
               h.hospital_name
        FROM donation_responses dr
        JOIN blood_requests br ON br.request_id = dr.request_id
        JOIN hospitals h ON h.hospital_id = br.hospital_id
        WHERE dr.donor_id = %s
        ORDER BY dr.updated_at DESC
        """,
        (donor_id,),
    )


def upsert_hospital_for_user(user_id, hospital_name, city, contact):
    existing = fetch_one("SELECT hospital_id FROM hospitals WHERE user_id = %s", (user_id,))
    if existing:
        execute(
            "UPDATE hospitals SET hospital_name = %s, city = %s, contact = %s WHERE user_id = %s",
            (hospital_name, city, contact, user_id),
        )
        return existing["hospital_id"]

    return execute(
        "INSERT INTO hospitals (user_id, hospital_name, city, contact) VALUES (%s, %s, %s, %s)",
        (user_id, hospital_name, city, contact),
    )


def get_hospital_by_user(user_id):
    return fetch_one(
        """
        SELECT h.*, u.email
        FROM hospitals h
        JOIN users u ON u.id = h.user_id
        WHERE h.user_id = %s
        """,
        (user_id,),
    )


def create_blood_request(hospital_id, blood_group, quantity, urgency, city):
    return execute(
        """
        INSERT INTO blood_requests (hospital_id, blood_group, quantity, urgency, city, request_status)
        VALUES (%s, %s, %s, %s, %s, 'Open')
        """,
        (hospital_id, blood_group, quantity, urgency, city),
    )


def get_requests_for_hospital(hospital_id):
    return fetch_all(
        """
        SELECT * FROM blood_requests
        WHERE hospital_id = %s
        ORDER BY created_at DESC
        """,
        (hospital_id,),
    )


def get_donation_responses_for_hospital(hospital_id):
    return fetch_all(
        """
        SELECT dr.*, br.blood_group, br.quantity, br.urgency, br.city, br.request_status,
               d.phone, d.user_id AS donor_user_id, u.name AS donor_name, u.email AS donor_email
        FROM donation_responses dr
        JOIN blood_requests br ON br.request_id = dr.request_id
        JOIN donors d ON d.donor_id = dr.donor_id
        JOIN users u ON u.id = d.user_id
        WHERE br.hospital_id = %s
        ORDER BY FIELD(dr.response_status, 'Pending', 'Accepted', 'Contacted', 'Scheduled', 'Completed', 'Rejected'),
                 dr.updated_at DESC
        """,
        (hospital_id,),
    )


def get_donation_response_for_hospital(response_id, hospital_id):
    return fetch_one(
        """
        SELECT dr.*, br.hospital_id, br.blood_group, br.request_id, br.quantity,
               d.user_id AS donor_user_id, d.donor_id, u.name AS donor_name
        FROM donation_responses dr
        JOIN blood_requests br ON br.request_id = dr.request_id
        JOIN donors d ON d.donor_id = dr.donor_id
        JOIN users u ON u.id = d.user_id
        WHERE dr.response_id = %s AND br.hospital_id = %s
        """,
        (response_id, hospital_id),
    )


def update_donation_response_status(response_id, hospital_id, status):
    execute(
        """
        UPDATE donation_responses dr
        JOIN blood_requests br ON br.request_id = dr.request_id
        SET dr.response_status = %s
        WHERE dr.response_id = %s AND br.hospital_id = %s
        """,
        (status, response_id, hospital_id),
    )


def update_request_status(request_id, hospital_id, status):
    execute(
        "UPDATE blood_requests SET request_status = %s WHERE request_id = %s AND hospital_id = %s",
        (status, request_id, hospital_id),
    )


def find_matching_donors(blood_group, city):
    return fetch_all(
        """
        SELECT d.*, u.name, u.email
        FROM donors d
        JOIN users u ON u.id = d.user_id
        WHERE d.blood_group = %s AND d.city = %s AND d.eligibility_status = 'Eligible'
        ORDER BY d.last_donation_date IS NULL DESC, d.last_donation_date ASC
        """,
        (blood_group, city),
    )


def get_inventory():
    return fetch_all("SELECT * FROM blood_inventory ORDER BY blood_group")


def update_inventory(blood_group, units_available):
    existing = fetch_one("SELECT inventory_id FROM blood_inventory WHERE blood_group = %s", (blood_group,))
    if existing:
        execute(
            "UPDATE blood_inventory SET units_available = %s, updated_at = CURRENT_TIMESTAMP WHERE blood_group = %s",
            (units_available, blood_group),
        )
        return existing["inventory_id"]
    return execute(
        "INSERT INTO blood_inventory (blood_group, units_available) VALUES (%s, %s)",
        (blood_group, units_available),
    )


def add_inventory_units(blood_group, units):
    existing = fetch_one("SELECT inventory_id, units_available FROM blood_inventory WHERE blood_group = %s", (blood_group,))
    if existing:
        execute(
            "UPDATE blood_inventory SET units_available = units_available + %s, updated_at = CURRENT_TIMESTAMP WHERE blood_group = %s",
            (units, blood_group),
        )
        return existing["inventory_id"]
    return execute(
        "INSERT INTO blood_inventory (blood_group, units_available) VALUES (%s, %s)",
        (blood_group, units),
    )


def create_notification(user_id, title, message, link=None):
    return execute(
        """
        INSERT INTO notifications (user_id, title, message, link)
        VALUES (%s, %s, %s, %s)
        """,
        (user_id, title, message, link),
    )


def get_recent_notifications(user_id, limit=5):
    return fetch_all(
        """
        SELECT * FROM notifications
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT %s
        """,
        (user_id, limit),
    )


def get_unread_notification_count(user_id):
    return fetch_one(
        "SELECT COUNT(*) AS total FROM notifications WHERE user_id = %s AND is_read = FALSE",
        (user_id,),
    )["total"]


def mark_notifications_read(user_id):
    execute("UPDATE notifications SET is_read = TRUE WHERE user_id = %s", (user_id,))


def get_recent_donations(limit=25):
    return fetch_all(
        """
        SELECT dn.*, u.name, d.city
        FROM donations dn
        JOIN donors d ON d.donor_id = dn.donor_id
        JOIN users u ON u.id = d.user_id
        ORDER BY dn.donation_date DESC, dn.donation_id DESC
        LIMIT %s
        """,
        (limit,),
    )


def admin_metrics():
    return {
        "donors": fetch_one("SELECT COUNT(*) AS total FROM donors")["total"],
        "hospitals": fetch_one("SELECT COUNT(*) AS total FROM hospitals")["total"],
        "requests": fetch_one("SELECT COUNT(*) AS total FROM blood_requests")["total"],
        "open_requests": fetch_one("SELECT COUNT(*) AS total FROM blood_requests WHERE request_status = 'Open'")["total"],
        "responses": fetch_one("SELECT COUNT(*) AS total FROM donation_responses")["total"],
    }


def get_all_users():
    return fetch_all("SELECT id, name, email, role, created_at FROM users ORDER BY created_at DESC")


def get_all_requests():
    return fetch_all(
        """
        SELECT br.*, h.hospital_name
        FROM blood_requests br
        JOIN hospitals h ON h.hospital_id = br.hospital_id
        ORDER BY br.created_at DESC
        """
    )


def get_all_donation_responses():
    return fetch_all(
        """
        SELECT dr.*, br.blood_group, br.quantity, br.urgency, br.city,
               h.hospital_name, u.name AS donor_name
        FROM donation_responses dr
        JOIN blood_requests br ON br.request_id = dr.request_id
        JOIN hospitals h ON h.hospital_id = br.hospital_id
        JOIN donors d ON d.donor_id = dr.donor_id
        JOIN users u ON u.id = d.user_id
        ORDER BY dr.updated_at DESC
        """
    )
