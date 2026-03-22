# MediStore

A modern full-stack online pharmacy platform built with Django, Django REST Framework, MySQL, and vanilla JavaScript.

MediStore supports product browsing, prescriptions, cart and checkout flows, order tracking, coupon discounts, Razorpay payment integration, admin insights, and progressive web app behavior.

## Highlights

- Secure authentication (token + session support)
- Product catalog with search, filtering, and autocomplete
- Cart and checkout with stock-aware order creation
- Order lifecycle management and return workflow
- Coupon system (fixed and percentage discounts)
- Prescription upload and admin review workflow
- Product review system restricted to purchased products
- Razorpay online payment integration + callback verification
- Admin dashboards with operational stats and chart endpoint
- Password reset flow and email notifications
- PWA support (service worker + manifest + offline page)

## Tech Stack

- Backend: Django 4.2, Django REST Framework
- Database: MySQL
- Frontend: HTML, CSS, vanilla JavaScript (template-driven)
- Media: Pillow
- Payments: Razorpay
- Config: django-environ

## Project Structure

```text
MediStore/
├─ medicare_backend/
│  ├─ manage.py
│  ├─ requirements.txt
│  ├─ start-dev.ps1
│  ├─ api/
│  └─ config/
├─ templates/
├─ static/
├─ RUN.md
└─ README.md
```

## Quick Start (Windows)

### 1. Go to backend folder

```powershell
Set-Location "c:/Users/Anil Jha/Desktop/flaming/MediStore/medicare_backend"
```

### 2. Install dependencies

```powershell
& "C:/Users/Anil Jha/AppData/Local/Programs/Python/Python39/python.exe" -m pip install -r requirements.txt
```

### 3. Create environment file

Create a file named `.env` inside `medicare_backend/` and add:

```env
SECRET_KEY=replace-with-strong-secret
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_ENGINE=django.db.backends.mysql
DB_NAME=medistore_db
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=127.0.0.1
DB_PORT=3306

EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@medistore.local

RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=
```

### 4. Apply migrations

```powershell
& "C:/Users/Anil Jha/AppData/Local/Programs/Python/Python39/python.exe" manage.py migrate
```

### 5. Seed sample data (optional)

```powershell
& "C:/Users/Anil Jha/AppData/Local/Programs/Python/Python39/python.exe" manage.py seed_sample_data --if-empty
```

### 6. Run the server

Recommended:

```powershell
.\start-dev.ps1
```

Manual:

```powershell
& "C:/Users/Anil Jha/AppData/Local/Programs/Python/Python39/python.exe" manage.py runserver 127.0.0.1:8000
```

Open: http://127.0.0.1:8000/

## API Overview

Base path: `/api/`

Main resources:

- `auth/login/`, `auth/register/`
- `products/`, `categories/`
- `cart/`, `cart/add_item/`, `cart/update_item/`, `cart/remove_item/`
- `orders/` with actions for payment, status updates, and returns
- `prescriptions/`
- `addresses/`
- `reviews/`
- `apply_coupon/`

## Security Notes

- Never commit real secrets in `.env`
- Use strong `SECRET_KEY` and production-safe `DEBUG=False`
- Restrict `ALLOWED_HOSTS` in production
- Set real email backend and sender identity
- Store Razorpay keys securely in environment variables

## Operational Commands

```powershell
# Django health check
& "C:/Users/Anil Jha/AppData/Local/Programs/Python/Python39/python.exe" manage.py check

# Create superuser
& "C:/Users/Anil Jha/AppData/Local/Programs/Python/Python39/python.exe" manage.py createsuperuser
```

## Current Status

Core backend API flow and key frontend routes have been smoke-tested and verified.

## Contributing

1. Create a feature branch
2. Make focused changes with clear commit messages
3. Run checks before opening a pull request
4. Submit PR with summary and testing notes

## License

This project is currently unlicensed. Add a license file (for example MIT) before public distribution.
