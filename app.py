from flask import Flask, render_template_string, request, session, redirect
import sqlite3, os, uuid

app = Flask(__name__)
app.secret_key = "kaswa_pro_max_full"

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

    c.execute("""
    CREATE TABLE IF NOT EXISTS orders(
        id TEXT PRIMARY KEY,
        username TEXT,
        items TEXT,
        total INTEGER,
        status TEXT,
        lat REAL,
        lng REAL
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- STYLE (AMAZON + FLIPKART HYBRID) ----------------
STYLE = """
<style>
body{margin:0;font-family:Arial;background:#f1f3f6}

/* AMAZON TOP BAR */
.nav{
background:#131921;
color:white;
padding:15px;
text-align:center;
font-size:22px;
font-weight:bold;
}

/* FLIPKART SUB BAR */
.subnav{
background:#2874f0;
color:white;
padding:10px;
text-align:center;
}

/* SEARCH */
.search{
text-align:center;
padding:10px;
background:white;
}
.search input{
width:70%;
padding:10px;
border-radius:6px;
border:1px solid #ccc;
}

/* PRODUCTS */
.container{
display:flex;
flex-wrap:wrap;
justify-content:center;
gap:15px;
padding:15px;
}

.card{
background:white;
width:180px;
padding:10px;
border-radius:10px;
text-align:center;
box-shadow:0 0 6px rgba(0,0,0,0.1);
}

.card:hover{transform:scale(1.03);transition:0.2s}

.btn{
background:#ff9f00;
border:none;
padding:8px;
border-radius:6px;
font-weight:bold;
cursor:pointer;
width:100%;
}

.btn:hover{background:#fb641b}

img{
width:100%;
height:120px;
object-fit:cover;
border-radius:8px;
}
</style>
"""

# ---------------- HOME ----------------
HOME = STYLE + """
<div class="nav">💎 KASWA PRO MAX STORE</div>
<div class="subnav">Amazon Reliability • Flipkart Offers • Beads Store</div>

<div class="search">
<input placeholder="Search products...">
</div>

<div style="text-align:center;padding:30px">
<h2>Welcome to KASWA</h2>
<p>Premium Beads • Jewellery • Handmade Products</p>

<a href="/shop"><button class="btn">Start Shopping</button></a>
<a href="/orders"><button class="btn">Track Orders 🚚</button></a>
</div>
"""

# ---------------- SHOP ----------------
SHOP = STYLE + """
<div class="nav">🛍️ SHOP</div>

<div class="search">
<input placeholder="Search beads...">
</div>

<div class="container">

{% for p in products %}
<div class="card">
<img src="{{p[3]}}">
<h3>{{p[1]}}</h3>
<p style="color:green;font-weight:bold">₹{{p[2]}}</p>
<a href="/add/{{p[0]}}"><button class="btn">Add to Cart</button></a>
</div>
{% endfor %}

</div>

<div style="text-align:center">
<a href="/cart"><button class="btn">Go to Cart 🛒</button></a>
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
<a href="/checkout"><button class="btn">Checkout</button></a>
</div>
"""

# ---------------- CHECKOUT ----------------
CHECKOUT = STYLE + """
<div class="nav">💳 PAYMENT</div>

<div style="text-align:center;padding:20px">
<h2>Total: ₹{{total}}</h2>

<a href="upi://pay?pa={{upi}}&pn=KASWA&am={{total}}&cu=INR">
<button class="btn">Pay Now</button>
</a>
</div>
"""

# ---------------- ORDERS ----------------
ORDERS = STYLE + """
<div class="nav">🚚 ORDER TRACKING</div>

<div class="container">

{% for o in orders %}
<div class="card">
<h3>Order ID</h3>
<p>{{o[0]}}</p>

<p><b>Status:</b> {{o[4]}}</p>
<p><b>Total:</b> ₹{{o[3]}}</p>

<a href="/track/{{o[0]}}">
<button class="btn">Track Map</button>
</a>
</div>
{% endfor %}

</div>
"""

# ---------------- TRACK MAP ----------------
TRACK = STYLE + """
<div class="nav">📍 LIVE DELIVERY TRACKING</div>

<h3 style="text-align:center">Status: {{order[4]}}</h3>

<iframe width="100%" height="400"
src="https://www.openstreetmap.org/export/embed.html?bbox={{order[6]-0.01}}%2C{{order[5]-0.01}}%2C{{order[6]+0.01}}%2C{{order[5]+0.01}}&layer=mapnik">
</iframe>

<div style="text-align:center">
<a href="/orders"><button class="btn">Back</button></a>
</div>
"""

# ---------------- CART ----------------
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
    cart.append(item)
    return redirect("/shop")

@app.route("/cart")
def cart_view():
    total = sum(i[1] for i in cart)
    return render_template_string(CART, items=cart, total=total)

@app.route("/checkout")
def checkout():
    total = sum(i[1] for i in cart)
    order_id = str(uuid.uuid4())[:8]

    conn = sqlite3.connect("kaswa.db")
    c = conn.cursor()
    c.execute("""
    INSERT INTO orders VALUES (?,?,?,?,?,?,?)
    """, (order_id, "user", str(cart), total, "Processing", 12.9716, 77.5946))
    conn.commit()
    conn.close()

    cart.clear()

    return render_template_string(CHECKOUT, total=total, upi=UPI_ID)

@app.route("/orders")
def orders():
    conn = sqlite3.connect("kaswa.db")
    c = conn.cursor()
    c.execute("SELECT * FROM orders")
    data = c.fetchall()
    conn.close()
    return render_template_string(ORDERS, orders=data)

@app.route("/track/<order_id>")
def track(order_id):
    conn = sqlite3.connect("kaswa.db")
    c = conn.cursor()
    c.execute("SELECT * FROM orders WHERE id=?", (order_id,))
    order = c.fetchone()
    conn.close()

    return render_template_string(TRACK, order=order)

# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)