from flask import Flask, request, redirect, session, render_template_string, jsonify
import sqlite3, json, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "kaswa_single_file"

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect("kaswa.db")
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price INTEGER,
        image TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        items TEXT,
        total INTEGER,
        status TEXT,
        created_at TEXT
    )""")

    # demo products
    c.execute("SELECT COUNT(*) FROM products")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO products(name,price,image) VALUES('Beads Pack',199,'https://via.placeholder.com/200')")
        c.execute("INSERT INTO products(name,price,image) VALUES('Premium Beads',399,'https://via.placeholder.com/200')")

    conn.commit()
    conn.close()

init_db()

cart = []

# ---------------- STYLE ----------------
STYLE = """
<style>
body{margin:0;font-family:Arial;background:#f1f3f6}
.top{background:#2874f0;color:white;padding:15px;display:flex;justify-content:space-between}
.container{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:15px;padding:20px}
.card{background:white;padding:10px;border-radius:10px;text-align:center}
img{width:100%;height:150px;object-fit:cover}
.btn{background:#ff9f00;border:none;padding:10px;border-radius:6px;font-weight:bold;cursor:pointer}
.box{padding:20px}
.chat{position:fixed;bottom:20px;right:20px;width:250px;background:white;border-radius:10px;box-shadow:0 0 10px gray;padding:10px}
</style>
"""

# ---------------- HOME ----------------
@app.route("/")
def home():
    conn = sqlite3.connect("kaswa.db")
    c = conn.cursor()
    c.execute("SELECT * FROM products")
    products = c.fetchall()
    conn.close()

    return STYLE + """
<div class="top">
<h2>KASWA STORE</h2>
<div>
<a href="/cart" style="color:white">Cart</a> |
<a href="/orders" style="color:white">Orders</a>
</div>
</div>

<div class="container">
""" + "".join([
f"""
<div class="card">
<img src="{p[3]}">
<h3>{p[1]}</h3>
<p>₹{p[2]}</p>
<a href="/add/{p[0]}"><button class="btn">Add</button></a>
</div>
"""
for p in products
]) + """
</div>

<!-- CHAT BOX -->
<div class="chat">
<form method="POST" action="/chat">
<input name="msg" placeholder="Ask AI..." style="width:100%">
<button class="btn">Send</button>
</form>
</div>
"""

# ---------------- ADD TO CART ----------------
@app.route("/add/<int:id>")
def add(id):
    conn = sqlite3.connect("kaswa.db")
    c = conn.cursor()
    c.execute("SELECT name,price FROM products WHERE id=?", (id,))
    item = c.fetchone()
    conn.close()

    cart.append(item)
    return redirect("/")

# ---------------- CART ----------------
@app.route("/cart")
def cart_page():
    total = sum(i[1] for i in cart)

    return STYLE + """
<div class="top"><h2>Your Cart</h2></div>

<div class="box">
""" + "".join([f"<p>{i[0]} - ₹{i[1]}</p>" for i in cart]) + f"""
<h3>Total: ₹{total}</h3>
<a href="/checkout"><button class="btn">Checkout</button></a>
</div>
"""

# ---------------- CHECKOUT ----------------
@app.route("/checkout")
def checkout():
    if "user" not in session:
        return redirect("/login")

    total = sum(i[1] for i in cart)

    conn = sqlite3.connect("kaswa.db")
    c = conn.cursor()

    c.execute("""
    INSERT INTO orders(username,items,total,status,created_at)
    VALUES(?,?,?,?,?)
    """, (session["user"], json.dumps(cart), total, "Processing", str(datetime.now())))

    conn.commit()
    conn.close()

    cart.clear()

    return redirect("/orders")

# ---------------- ORDERS ----------------
@app.route("/orders")
def orders():
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("kaswa.db")
    c = conn.cursor()
    c.execute("SELECT * FROM orders WHERE username=?", (session["user"],))
    data = c.fetchall()
    conn.close()

    return STYLE + """
<div class="top"><h2>My Orders</h2></div>

<div class="box">
""" + "".join([
f"""
<div class="card">
<h3>Order #{o[0]}</h3>
<p>Status: {o[4]}</p>
<p>Total: ₹{o[3]}</p>
<p>Date: {o[5]}</p>
</div>
"""
for o in data
]) + """
</div>
"""

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET","POST"])
def login():
    return render_template_string(LOGIN_UI)

@app.route("/do_login", methods=["POST"])
def do_login():
    u = request.form["username"]
    p = request.form["password"]

    conn = sqlite3.connect("kaswa.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (u,p))
    user = c.fetchone()
    conn.close()

    if user:
        session["user"] = u
        return redirect("/")
    return "Invalid Login"

@app.route("/signup", methods=["POST"])
def signup():
    u = request.form["username"]
    p = request.form["password"]

    conn = sqlite3.connect("kaswa.db")
    c = conn.cursor()
    c.execute("INSERT INTO users(username,password) VALUES(?,?)", (u,p))
    conn.commit()
    conn.close()

    return redirect("/login")

# ---------------- LOGIN UI ----------------
LOGIN_UI = """
<style>
body{margin:0;font-family:Arial;background:#0f172a;display:flex;justify-content:center;align-items:center;height:100vh;color:white}
.box{background:rgba(255,255,255,0.06);padding:25px;border-radius:15px;width:320px;text-align:center}
input{width:90%;padding:10px;margin:8px;border:none;border-radius:8px}
.btn{width:95%;padding:10px;background:#ff9f00;border:none;border-radius:8px;font-weight:bold}
</style>

<div class="box">
<h2>KASWA LOGIN</h2>

<form method="POST" action="/do_login">
<input name="username" placeholder="Username">
<input name="password" type="password" placeholder="Password">
<button class="btn">Login</button>
</form>

<br>

<form method="POST" action="/signup">
<input name="username" placeholder="New Username">
<input name="password" type="password" placeholder="New Password">
<button class="btn">Signup</button>
</form>
</div>
"""

# ---------------- AI CHAT ----------------
@app.route("/chat", methods=["POST"])
def chat():
    msg = request.form.get("msg","").lower()

    if "order" in msg:
        reply = "📦 Check orders page."
    elif "delivery" in msg:
        reply = "🚚 Delivery in 3-5 days."
    elif "refund" in msg:
        reply = "💰 Refund in 5-7 days."
    elif "hi" in msg:
        reply = "👋 Hello! Welcome to KASWA."
    else:
        reply = "🤖 I can help with orders, delivery, refunds."

    return f"<script>alert('{reply}');window.location='/'</script>"

# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0", port=port)