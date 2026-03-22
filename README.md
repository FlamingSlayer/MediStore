# 💊 MediStore – Online Pharmacy Platform

> A full‑stack e‑pharmacy solution that lets users browse medicines, upload prescriptions, manage orders, and track deliveries. The system provides separate dashboards for customers and administrators, handles coupon discounts, integrates Razorpay payments, and works as a Progressive Web App (PWA).

---

## ✨ Features

### 👤 For Customers
- Secure registration / login with token‑based authentication
- Browse medicines with search, filters (category, Rx/OTC, price range), and autocomplete
- View detailed product information, reviews, and ratings
- Add to cart, adjust quantities, and proceed to checkout
- Apply coupon codes for discounts
- Upload prescriptions and track review status
- Manage saved delivery addresses
- Place orders (COD or online via Razorpay)
- Track order lifecycle (placed → confirmed → shipped → delivered)
- Request order cancellation / return
- View order history and download past prescriptions

### 👑 For Administrators
- Dedicated admin dashboard with key metrics (orders, users, revenue, pending prescriptions)
- Full product management (add, edit, delete products)
- Order management: update status, view details, process cancellations/returns
- User management: list all users, promote to staff
- Prescription review: approve or reject with notes
- Inventory overview and low‑stock alerts (optional)

### 🛠️ Additional Capabilities
- Email notifications (welcome, order confirmation, status changes, prescription review)
- Password reset via email
- Progressive Web App (PWA) – installable on mobile devices
- Admin dashboard chart (monthly orders/revenue) using Chart.js
- Product reviews (only users who purchased can review)

---

## 🏗️ System Architecture

```
Browser (HTML/CSS/JS)
        │
        ▼
Django Backend (DRF)
        │
        ▼
MySQL Database
```

---

## 🛠️ Tech Stack

| Layer        | Technology                         | Purpose                          |
|--------------|------------------------------------|----------------------------------|
| **Frontend** | HTML5, CSS3, Vanilla JavaScript    | User interface, dynamic content  |
| **Backend**  | Django, Django REST Framework (DRF)| API development, business logic  |
| **Database** | MySQL                              | Data persistence                 |
| **Auth**     | DRF TokenAuthentication            | Secure API access                |
| **Payments** | Razorpay                           | Online payment processing        |
| **Styling**  | Custom CSS (responsive, dark mode) | Modern, accessible UI            |
| **Icons**    | Font Awesome 6                     | Visual enhancements              |
| **PWA**      | Service Worker + Manifest          | Offline support, installability  |

---

## 📁 Project Structure

```
MediStore/
├── medicare_backend/           # Django backend application
│   ├── api/                    # DRF API app (models, views, serializers)
│   ├── config/                 # Django settings, urls
│   ├── manage.py
│   ├── requirements.txt
│   ├── start-dev.ps1           # PowerShell launcher (Windows)
│   └── .env                    # Environment variables
├── static/                     # Static assets (CSS, JS, SVG)
│   ├── css/
│   │   └── styles.css          # Main stylesheet
│   ├── js/
│   │   ├── app.js              # Core utilities & API helpers
│   │   ├── config.js           # API configuration
│   │   └── init.js             # Global initialization
│   ├── manifest.json           # PWA manifest
│   ├── service-worker.js       # Offline support
│   └── icons/                  # App icons (192x192, 512x512)
├── templates/                  # HTML templates
│   ├── index.html              # Landing page
│   ├── products.html           # Product listing
│   ├── product-detail.html     # Single product view
│   ├── cart.html               # Shopping cart
│   ├── checkout.html           # Checkout flow
│   ├── dashboard.html          # Customer dashboard
│   ├── admin.html              # Admin dashboard
│   ├── login.html              # Login page
│   ├── register.html           # Registration page
│   ├── upload-prescription.html# Prescription upload
│   ├── order-detail.html       # Order details & tracking
│   └── order-success.html      # Order confirmation
├── RUN.md                      # Detailed run instructions
├── .gitignore
└── README.md                   # This file
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- pip
- MySQL 5.7+ (or SQLite for development)
- Git

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/FlamingSlayer/MediStore.git
cd MediStore/medicare_backend
```

### 2️⃣ Set Up Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment

Create a `.env` file in `medicare_backend/` directory:

```env
SECRET_KEY=your-strong-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_ENGINE=django.db.backends.mysql
DB_NAME=medistore_db
DB_USER=root
DB_PASSWORD=yourpassword
DB_HOST=127.0.0.1
DB_PORT=3306

EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@medistore.local

RAZORPAY_KEY_ID=your_test_key_id
RAZORPAY_KEY_SECRET=your_test_secret
```

### 5️⃣ Run Database Migrations

```bash
python manage.py migrate
python manage.py createsuperuser    # Create admin user
```

### 6️⃣ Seed Sample Data (Optional)

```bash
python manage.py seed_sample_data --if-empty
```

### 7️⃣ Start Development Server

```bash
# Recommended (Windows)
.\start-dev.ps1

# Manual
python manage.py runserver 127.0.0.1:8000
```

Open:
- Main app: http://127.0.0.1:8000
- Admin panel: http://127.0.0.1:8000/admin

---

## 📚 API Overview

**Base path:** `/api/`  
**Authentication:** DRF Token (header: `Authorization: Token <token>`)

| Endpoint | Methods | Description |
|----------|---------|-------------|
| `/auth/login/` | POST | Login, returns auth token |
| `/auth/register/` | POST | Register new user |
| `/products/` | GET, POST | List / create products |
| `/products/featured/` | GET | Discounted products |
| `/products/{id}/autocomplete/` | GET | Search autocomplete |
| `/categories/` | GET | Product categories |
| `/cart/` | GET | View user's cart |
| `/cart/add_item/` | POST | Add product to cart |
| `/cart/update_item/` | POST | Update item quantity |
| `/cart/remove_item/` | POST | Remove item from cart |
| `/orders/` | GET, POST | List orders / create from cart |
| `/orders/{id}/create_payment/` | POST | Create Razorpay payment |
| `/orders/{id}/payment_callback/` | POST | Razorpay callback handler |
| `/orders/{id}/update_status/` | POST | Change order status |
| `/orders/{id}/request_return/` | POST | Request return |
| `/prescriptions/` | GET, POST | List / upload prescriptions |
| `/prescriptions/{id}/` | PATCH | Review prescription (admin) |
| `/addresses/` | GET, POST | Manage delivery addresses |
| `/reviews/` | GET, POST | Product reviews |
| `/apply_coupon/` | POST | Validate & apply coupon |
| `/admin/users/` | GET | List all users (admin only) |
| `/admin/stats/` | GET | Dashboard statistics |
| `/admin/stats/chart/` | GET | Monthly orders/revenue chart |

---

## 🧪 Testing

```bash
python manage.py check              # Django health check
python manage.py test               # Run all tests
python manage.py test api           # Run API tests only
```

---

## 🚢 Deployment

### Render / Railway / PythonAnywhere
1. Push code to GitHub repository
2. Set environment variables in platform dashboard
3. Configure MySQL database (cloud service or managed)
4. Update `ALLOWED_HOSTS` and set `DEBUG=False`
5. Collect static files:
   ```bash
   python manage.py collectstatic
   ```
6. Use production WSGI server:
   ```bash
   gunicorn config.wsgi:application
   ```
7. Configure media folder for uploads

---

## 🔐 Security Notes

- ⚠️ **Never commit** `.env` file – it contains secrets
- In production, set `DEBUG=False` and restrict `ALLOWED_HOSTS`
- Use strong passwords and rotate secret keys regularly
- Store payment keys securely in environment variables only
- For production email, configure a real SMTP backend
- Enable HTTPS in production
- Use secure session cookies: `SESSION_COOKIE_SECURE=True`
- Add CSRF protection and rate limiting as needed

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m "Add your feature"`
4. Push to branch: `git push origin feature/your-feature`
5. Open a Pull Request with a clear description

---

## 👥 Default Test Users

After seeding sample data, log in with:

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@example.com | admin123 |
| Customer | customer@example.com | customer123 |

---

## 🙏 Acknowledgments

- Django & Django REST Framework community
- Razorpay for payment gateway
- FontAwesome for icons
- All contributors and testers

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/FlamingSlayer/MediStore/issues)
- **Discussions:** [GitHub Discussions](https://github.com/FlamingSlayer/MediStore/discussions)

---

## 📄 License

This project is currently unlicensed. Add a LICENSE file before public distribution (recommend MIT or Apache 2.0).

---

**Built with ❤️ by VidhyanJha**

If you find this project useful, please give it a ⭐ on GitHub!
