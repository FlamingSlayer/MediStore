# MediStore Run Guide (Windows)

## 1. Open backend folder

```powershell
Set-Location "c:/Users/......./MediStore_Backend"
```

## 2. Install dependencies

```powershell
./venv/Scripts/python.exe -m pip install -r requirements.txt
```

## 3. Configure environment

- Copy values from `.env.example` into `.env`.
- Keep MySQL settings in `.env`.

## 4. Apply migrations

```powershell
./venv/Scripts/python.exe manage.py migrate
```

## 5. Seed sample data (optional)

```powershell
./venv/Scripts/python.exe manage.py seed_sample_data --if-empty
```

## 6. Start server (recommended)

```powershell
.\start-dev.ps1
```

## 7. Start server (manual)

```powershell
./venv/Scripts/python.exe manage.py runserver 127.0.0.1:8000
```

## 8. Verify backend health

```powershell
./venv/Scripts/python.exe manage.py check
```
