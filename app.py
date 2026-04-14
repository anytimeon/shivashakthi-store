from flask import Flask, render_template_string, request, session, redirect
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "kaswa_final_secret"

UPI_ID = "princeveguru@ibl"

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect("kaswa.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price INTEGER,
        image TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- STYLE ----------------
STYLE = """
<style>
body{margin:0;font-family:Arial;background:#0f172a;color:white}

.nav{background:#111827;padding:15px;text-align:center;font-size:22px;font-weight:bold;color:gold}

.container{display:flex;flex-wrap:wrap;justify-content:center;gap:15px;padding:20px}

.card{background:#1f2937;width:200px;padding:10px;border-radius:12px;text-align:center}

.btn{background:#f59e0b;border:none;padding:10px;border-radius:10px;font-weight:bold;cursor:pointer}

.btn:hover{background:#fbbf24}

input{padding:8px;margin:5px;border-radius:8px;border:none;width:80%}

img{width:100%;height:120px;object-fit:cover;border-radius:8px}
</style>
"""

# ---------------- HOME ----------------
HOME = STYLE + """
<div class="nav">💎 KASWA STORE</div>

<div style="text-align:center;padding:40px">
<h2>Premium Beads Store</h2>

<a href="/shop"><button class="btn">Shop</button></a>
<a href="/login"><button class="btn">Login</button></a>
<a href="/admin"><button class="btn">Admin</button></a>
</div>
"""

# ---------------- SHOP ----------------
SHOP = STYLE + """
<div class="nav">🛍️ SHOP</div>

<div class="container">

{% for p in products %}
<div class="card">
<img src="{{p[3] if p[3] else 'https://via.placeholder.com/150'}}">
<h3>{{p[1]}}</h3>
<p>₹{{p[2]}}</p>
<a href="/add/{{p[0]}}"><button class="btn">Add</button></a>
</div>
{% endfor %}

</div>

<div style="text-align:center">
<a href="/cart"><button class="btn">Cart 🛒</button></a>
</div>
"""

# ---------------- CART ----------------
CART = STYLE + """
<div class="nav">🛒 CART</div>

<div class="container">

{% for i in items %}
<div class="card">
<p>{{i[0]}}</p>
<p>₹{{i[1]}}</p>
</div>
{% endfor %}

</div>

<h2 style="text-align:center">Total: ₹{{total}}</h2>

<div style="text-align:center">
<a href="upi://pay?pa={{upi}}&pn=KASWA&am={{total}}&cu=INR">
<button class="btn">Pay Now</button>
</a>
</div>
"""

# ---------------- LOGIN ----------------
LOGIN = STYLE + """
<div class="nav">🔐 LOGIN</div>

<div style="text-align:center;padding:30px">
<form method="POST">
<input name="username" placeholder="Username"><br>
<input name="password" placeholder="Password"><br>
<button class="btn">Login</button>
</form>
</div>
"""

# ---------------- ADMIN ----------------
ADMIN = STYLE + """
<div class="nav">⚙️ ADMIN PANEL</div>

<div style="text-align:center;padding:20px">

<form method="POST" action="/add_product">
<input name="name" placeholder="Product Name"><br>
<input name="price" placeholder="Price"><br>
<input name="image" placeholder="Image URL (optional)"><br>
<button class="btn">Add Product</button>
</form>

<h3>Products</h3>

{% for p in products %}
<p>{{p[1]}} - ₹{{p[2]}}</p>
{% endfor %}

</div>
"""

# ---------------- CART STORAGE ----------------
cart = []

# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return render_template_string(HOME)

@app.route("/shop")
def shop():
    conn = sqlite3.connect("kaswa.db")
    c = conn.cursor()
    c.execute("SELECT * FROM products")
    data = c.fetchall()
    conn.close()
    return render_template_string(SHOP, products=data)

@app.route("/add/<int:id>")
def add(id):
    conn = sqlite3.connect("kaswa.db")
    c = conn.cursor()
    c.execute("SELECT name,price FROM products WHERE id=?", (id,))
    item = c.fetchone()
    conn.close()

    if item:
        cart.append(item)

    return redirect("/shop")

@app.route("/cart")
def cart_view():
    total = sum(i[1] for i in cart)
    return render_template_string(CART, items=cart, total=total, upi=UPI_ID)

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        conn = sqlite3.connect("kaswa.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?",
                  (request.form["username"], request.form["password"]))
        user = c.fetchone()
        conn.close()

        if user:
            session["user"] = user[1]
            return redirect("/admin")

    return render_template_string(LOGIN)

# ---------------- ADMIN ----------------
@app.route("/admin")
def admin():
    if not session.get("user"):
        return redirect("/login")

    conn = sqlite3.connect("kaswa.db")
    c = conn.cursor()
    c.execute("SELECT * FROM products")
    data = c.fetchall()
    conn.close()

    return render_template_string(ADMIN, products=data)

@app.route("/add_product", methods=["POST"])
def add_product():
    if not session.get("user"):
        return redirect("/login")

    name = request.form["name"]
    price = request.form["price"]
    image = request.form["image"]

    conn = sqlite3.connect("kaswa.db")
    c = conn.cursor()
    c.execute("INSERT INTO products(name,price,image) VALUES(?,?,?)",
              (name, price, image))
    conn.commit()
    conn.close()

    return redirect("/admin")

# ---------------- RUN (IMPORTANT FOR RENDER) ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)