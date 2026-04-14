from flask import Flask, render_template_string, request, session, redirect
import sqlite3, os

app = Flask(__name__)
app.secret_key = "kaswa_big_ui_123"

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

# ---------------- BIG AMAZON STYLE ----------------
STYLE = """
<style>

body{
margin:0;
font-family:Arial;
background:linear-gradient(135deg,#0f172a,#1e293b,#0f172a);
color:white;
overflow-x:hidden;
}

/* ANIMATED HEADER */
.header{
background:linear-gradient(90deg,#ffcc00,#ff6600,#ffcc00);
padding:20px;
text-align:center;
font-size:34px;
font-weight:bold;
color:black;
letter-spacing:2px;
animation:glow 3s infinite;
}

@keyframes glow{
0%{box-shadow:0 0 10px #ffcc00}
50%{box-shadow:0 0 25px #ff6600}
100%{box-shadow:0 0 10px #ffcc00}
}

/* FLOATING BACKGROUND ANIMATION */
.bg-circle{
position:fixed;
width:200px;
height:200px;
background:rgba(255,215,0,0.1);
border-radius:50%;
animation:float 10s infinite;
}

@keyframes float{
0%{transform:translateY(0)}
50%{transform:translateY(100px)}
100%{transform:translateY(0)}
}

/* BUTTONS */
.btn{
background:#f59e0b;
border:none;
padding:14px 20px;
border-radius:12px;
font-size:16px;
font-weight:bold;
cursor:pointer;
margin:8px;
transition:0.3s;
}

.btn:hover{
transform:scale(1.1);
background:#ffd700;
}

/* PRODUCT GRID (BIG LIKE AMAZON) */
.container{
display:grid;
grid-template-columns:repeat(auto-fit,minmax(250px,1fr));
gap:20px;
padding:30px;
}

.card{
background:rgba(255,255,255,0.08);
backdrop-filter:blur(10px);
border-radius:18px;
padding:15px;
text-align:center;
box-shadow:0 0 15px rgba(255,255,255,0.1);
transition:0.3s;
}

.card:hover{
transform:scale(1.05);
box-shadow:0 0 25px #ffcc00;
}

img{
width:100%;
height:180px;
object-fit:cover;
border-radius:12px;
}

h2{
text-align:center;
font-size:28px;
margin-top:20px;
}

</style>
"""

# ---------------- HOME ----------------
HOME = STYLE + """
<div class="bg-circle" style="top:50px;left:30px"></div>
<div class="bg-circle" style="bottom:50px;right:30px"></div>

<div class="header">💎 KASWA STORE</div>

<h2>Premium Beads • Jewellery • Handmade Luxury</h2>

<div style="text-align:center">
<a href="/shop"><button class="btn">🛍️ Enter Store</button></a>
<a href="/login"><button class="btn">🔐 Login</button></a>
</div>
"""

# ---------------- SHOP ----------------
SHOP = STYLE + """
<div class="header">🛍️ KASWA MARKETPLACE</div>

<div class="container">

{% for p in products %}
<div class="card">
<img src="{{p[3]}}">
<h3>{{p[1]}}</h3>
<p style="color:#ffd700;font-size:18px">₹{{p[2]}}</p>
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
<div class="header">🛒 YOUR CART</div>

<div style="padding:20px;text-align:center">

{% for i in items %}
<p>{{i[0]}} - ₹{{i[1]}}</p>
{% endfor %}

<h2>Total: ₹{{total}}</h2>

<a href="upi://pay?pa={{upi}}&pn=KASWA&am={{total}}&cu=INR">
<button class="btn">💳 Pay Now</button>
</a>

</div>
"""

# ---------------- LOGIN ----------------
LOGIN = STYLE + """
<div class="header">🔐 LOGIN</div>

<div style="text-align:center;padding:40px">
<form method="POST">
<input name="username" placeholder="Username" style="padding:10px;width:250px"><br><br>
<input name="password" placeholder="Password" style="padding:10px;width:250px"><br><br>
<button class="btn">Login</button>
</form>
</div>
"""

# ---------------- DATA ----------------
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
    return render_template_string(CART, items=cart, total=total, upi=UPI_ID)

@app.route("/login", methods=["GET","POST"])
def login():
    return render_template_string(LOGIN)

# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)