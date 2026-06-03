from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from backend.bot import bot_state, WATCHLIST

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


# -----------------------
# UI
# -----------------------
@app.get("/", response_class=HTMLResponse)
def dashboard():

    prices_html = ""
    for code, data in bot_state["prices"].items():
        prices_html += f"""
        <div class="card">
            <b>{data['name']}</b><br>
            {code}<br>
            ¥{data['price']}
        </div>
        """

    watchlist_html = ""
    for k, v in WATCHLIST.items():
        watchlist_html += f"<li>{v} ({k})</li>"

    html = f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <link rel="manifest" href="/static/manifest.json">

        <style>
            body {{
                margin:0;
                font-family: Arial;
                background:#0f172a;
                color:white;
            }}

            .panel {{
                margin:10px;
                padding:12px;
                background:#1e293b;
                border-radius:12px;
            }}

            .card {{
                padding:10px;
                margin:5px;
                background:#334155;
                border-radius:10px;
            }}

            button {{
                width:100%;
                padding:12px;
                margin-top:10px;
                border-radius:10px;
                border:none;
            }}

            .btn {{
                background:#2563eb;
                color:white;
            }}

            .danger {{
                background:#dc2626;
                color:white;
            }}

            input {{
                width:100%;
                padding:10px;
                margin-top:5px;
            }}
        </style>

        <script>
        if ("serviceWorker" in navigator) {{
            navigator.serviceWorker.register("/static/sw.js");
        }}
        </script>

    </head>

    <body>

        <div class="panel">
            <h2>📈 STOCK BOT</h2>
            <p>損益: ¥{bot_state["today_pnl"]:,}</p>
        </div>

        <form action="/toggle" method="post">
            <div class="panel">
                <button class="btn">START / STOP</button>
            </div>
        </form>

        <!-- 銘柄追加 -->
        <div class="panel">
            <h3>銘柄追加</h3>
            <form action="/add-stock" method="post">
                <input name="code" placeholder="例: 7203.T">
                <input name="name" placeholder="例: Toyota">
                <button class="btn">追加</button>
            </form>
        </div>

        <!-- 利確・損切り -->
        <div class="panel">
            <h3>設定</h3>

            <form action="/set-risk" method="post">

                <label>利確 %</label>
                <input type="number" name="take_profit" value="2">

                <label>損切り %</label>
                <input type="number" name="stop_loss" value="-1">

                <button class="btn">保存</button>
            </form>
        </div>

        <!-- 銘柄 -->
        <div class="panel">
            <h3>監視銘柄</h3>
            {watchlist_html}
        </div>

        <!-- 価格 -->
        <div class="panel">
            <h3>価格</h3>
            {prices_html}
        </div>

    </body>
    </html>
    """

    return html


# -----------------------
# ON/OFF
# -----------------------
@app.post("/toggle")
def toggle():
    bot_state["enabled"] = not bot_state["enabled"]
    return RedirectResponse("/", 303)


# -----------------------
# 銘柄追加
# -----------------------
@app.post("/add-stock")
def add_stock(code: str = Form(...), name: str = Form(...)):
    WATCHLIST[code] = name
    return RedirectResponse("/", 303)


# -----------------------
# リスク設定
# -----------------------
@app.post("/set-risk")
def set_risk(take_profit: int = Form(...), stop_loss: int = Form(...)):
    bot_state["take_profit"] = take_profit
    bot_state["stop_loss"] = stop_loss
    return RedirectResponse("/", 303)