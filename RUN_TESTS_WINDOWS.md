# Запуск тестов на Windows

## Backend

```powershell
cd C:\Users\Asus\Desktop\lab5proj\server
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pytest -q
```

Если у тебя установлен Python 3.14 и `venv` ломается, поставь Python 3.12 и создай окружение так:

```powershell
py -3.12 -m venv .venv
```

## Frontend

```powershell
cd C:\Users\Asus\Desktop\lab5proj\client
npm install
npm run test
```

Если Rollup/Vite ругается на `@rollup/rollup-win32-x64-msvc`, выполни:

```powershell
taskkill /F /IM node.exe
rmdir /s /q node_modules
del package-lock.json
npm cache clean --force
npm install
npm install -D @rollup/rollup-win32-x64-msvc
npm run test
```

## E2E

```powershell
cd C:\Users\Asus\Desktop\lab5proj\client
npx playwright install
npm run test:e2e
```
