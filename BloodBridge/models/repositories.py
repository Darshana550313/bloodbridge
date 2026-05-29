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


def get_matching_requests(blood_group, city):
    return fetch_all(
        """
        SELECT br.*, h.hospital_name
        FROM blood_requests br
        JOIN hospitals h ON h.hospital_id = br.hospital_id
        WHERE br.blood_group = %s
          AND br.city = %s
          AND br.request_status IN ('Open', 'In Progress')
        ORDER BY FIELD(br.urgency, 'Critical', 'High', 'Medium', 'Low'), br.created_at DESC
        """,
        (blood_group, city),
    )


def create_donation(donor_id, donation_date, blood_group, units):
    return execute(
        """
        INSERT INTO donations (donor_id, donation_date, blood_group, units)
        VALUES (%s, %s, %s, %s)
        """,
        (donor_id, donation_date, blood_group, units),
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

