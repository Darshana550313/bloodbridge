# BloodBridge: Optimizing Lifesaving Resources using AWS EC2 and RDS

BloodBridge is a production-ready Flask + MySQL blood donation and emergency request management system. It supports donors, hospitals, blood banks, and administrators with role-based dashboards, request matching, stock analytics, flash alerts, and AWS deployment guidance.

## Features

- User registration, login, logout, password hashing, and session-based access control.
- Donor profile, blood group, city, phone, last donation date, eligibility checker, nearby requests, and donation scheduling.
- Hospital profile, emergency blood requests, urgency labels, matching donors, request status tracking, email notification hook, and SMS placeholder.
- Blood bank inventory update workflow, low stock alerts, and donation history.
- Admin dashboard with total donors, hospitals, requests, user management, emergency request tracking, and Chart.js inventory analytics.
- MySQL connection pooling with PyMySQL and DBUtils for AWS RDS.
- Bootstrap, Font Awesome, responsive red/white medical UI.

## Project Structure

```text
BloodBridge/
├── app.py
├── wsgi.py
├── config.py
├── requirements.txt
├── database.sql
├── README.md
├── AWS_DEPLOYMENT.md
├── routes/
├── models/
├── utils/
├── static/
│   ├── css/
│   ├── js/
│   └── images/
└── templates/
```

## Sample Accounts

All sample passwords are included for testing only. Change them before deployment.

| Role | Email | Password |
|---|---|---|
| Admin | `admin@bloodbridge.local` | `Admin@12345` |
| Donor | `donor@bloodbridge.local` | `Donor@12345` |
| Hospital | `hospital@bloodbridge.local` | `Hospital@12345` |
| Blood Bank | `bank@bloodbridge.local` | `Bank@12345` |

## API Explanation

- `GET /api/inventory`: returns inventory chart data as `{ labels: [], units: [] }`.
- `GET /api/requests`: returns emergency blood request records for authenticated users.

The app mostly uses server-rendered HTML forms because it is beginner-friendly and easy to deploy on EC2. The JSON endpoints power charts and can be extended for a mobile app or SPA.



