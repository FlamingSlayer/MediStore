# MediStore Run Guide (Windows)

## 1. Open backend folder

```powershell
Set-Location "c:/Users/......./MediStore_Backend"
```

## 2. Install dependencies

```powershell
& "C:/Users/..../AppData/Local/Programs/Python/Python39/python.exe" -m pip install -r requirements.txt
```

## 3. Configure environment

- Copy values from `.env.example` into `.env`.
- Keep MySQL settings in `.env`.

## 4. Apply migrations

```powershell
& "C:/Users/...../AppData/Local/Programs/Python/Python39/python.exe" manage.py migrate
```

## 5. Seed sample data (optional)

```powershell
& "C:/Users/...../AppData/Local/Programs/Python/Python39/python.exe" manage.py seed_sample_data --if-empty
```

## 6. Start server (recommended)

```powershell
.\start-dev.ps1
```

## 7. Start server (manual)

```powershell
& "C:/Users/....../AppData/Local/Programs/Python/Python39/python.exe" manage.py runserver 127.0.0.1:8000
```

## 8. Verify backend health

```powershell
& "C:/Users/Anil Jha/AppData/Local/Programs/Python/Python39/python.exe" manage.py check
```
