# local.dev — Local Test Server

Flask-based local API test server with a built-in browser UI.
Double-click the `.exe` - browser opens automatically. No setup required for the end user.

## Build the exe (one time)

```bash
pip install flask pyinstaller
python build.py
# → dist/local-dev-server.exe  (~25MB)
```

## Run without building

```bash
pip install flask
python server.py
```

## What's included

| Route | Method | Description |
|---|---|---|
| `/` | GET | Browser UI (request log + Try It) |
| `/api/hello` | GET | Health check / hello |
| `/api/echo` | POST | Echoes back your JSON body |
| `/api/items` | GET, POST | Example collection endpoint |
| `/*` | ANY | Catch-all (logs 404s) |

## Add your own routes

Edit the **"Your API routes"** section in `server.py`.
Call `_add_log(method, path, status, ip)` to make them show up in the UI.

## Tips

- Remove `--noconsole` from `build.py` if you want stdout logs visible in a terminal
- Use `--onedir` instead of `--onefile` for faster cold start
- Change `PORT = 3000` at the bottom of `server.py` to use a different port
