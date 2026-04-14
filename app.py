from flask import Flask, render_template_string, request, session, redirect
import os

app = Flask(__name__)
app.secret_key = "casva_pro_123"

UPI_ID = "princeveguru@ibl"

# ---------------- PRODUCTS ----------------
products = [
    {"id": 1, "name": "Swarovski Premium Beads", "price": 500},
    {"id": 2, "name": "Monalisa Designer Beads", "price": 150},
    {"id": 3, "name": "Hydra Crystal Beads", "price": 300},
    {"id": 4, "name": "Pearl Luxury Beads", "price": 200},
]

# ---------------- STYLE ----------------
STYLE = """
<style>
body{
margin:0;
font-family:Arial;
background:#0b0f19;
color:white;
}

.header{
background:linear-gradient(90deg,#ffcc00,#ff6600);
padding:15px;
text-align:center;
font-size:28px;
font-weight:bold;
color:black;
}

.banner{
background:url('https://images.unsplash.com/photo-1617038260897-41a1f14a8ca0') center;
background-size:cover;
padding:60px 20px;
text-align:center;
}

.banner h1{
font-size:40px;
text-shadow:0 0 10px black;
}

.btn{
padding:12px 18px;
margin:6px;
border:none;
border-radius:10px;
background:#00e5ff;
color:black;
font-weight:bold;
cursor:pointer;
}

.btn:hover{
background:#ffd700;
}

.container{
display:flex;
flex-wrap:wrap;
justify-content:center;
gap:15px;
padding:20px;
}

.card{
width:200px;
background:#151b2e;
border-radius:15px;
padding:10px;
text-align:center;
box-shadow:0 0 10px #00e5ff33;
transition:0.3s;
}

.card:hover{
transform:scale(1.05);
box-shadow:0 0 15px #00e5ff;
}

.price{
color:#ffd700;
font-weight:bold;
}

.footer{
text-align:center;
padding:10px;
color:#aaa;
}
</style>
"""

# ---------------- HOME ----------------
HOME = STYLE + """
<div class="header">💎 CASVA BEADS STORE</div>

<div class="banner">
<h1>Premium Beads Collection</h1>
<p>Luxury • Style • Creativity</p>
<a href="/shop"><button class="btn">Shop Now</button></a>
<a href="/cart"><button class="btn">Cart 🛒</button></a>
</div>

<div class="footer">CASVA © All Rights Reserved</div>
"""

# ---------------- SHOP ----------------
SHOP = STYLE + """
<div class="header">💎 CASVA COLLECTION</div>

<div class="container">

{% for p in products %}
<div class="card">
<h3>{{p.name}}</h3>
<p class="price">₹{{p.price}}</p>
<a href="/add/{{p.id}}"><button class="btn">Add to Cart</button></a>
</div>
{% endfor %}

</div>

<div style="text-align:center">
<a href="/cart"><button class="btn">Go to Cart 🛒</button></a>
</div>
"""

# ---------------- CART ----------------
CART = STYLE + """
<div class="header">🛒 CASVA CART</div>

<div style="text-align:center;padding:20px">

{% for i in items %}
<p>📿 {{i.name}} - ₹{{i.price}}</p>
{% endfor %}

<h2>Total: ₹{{total}}</h2>

<a href="upi://pay?pa={{upi}}&pn=CASVA&am={{total}}&cu=INR">
<button class="btn">💳 Pay Now</button>
</a>

<br><br>
<a href="/success"><button class="btn">✔ Place Order</button></a>

</div>
"""

# ---------------- SUCCESS ----------------
SUCCESS = STYLE + """
<div class="header">🎉 ORDER SUCCESS</div>

<div style="text-align:center;padding:30px">
<h2>Thank you for shopping at CASVA 💎</h2>

<a href="https://wa.me/91XXXXXXXXXX?text=I%20ordered%20from%20CASVA">
<button class="btn">📲 WhatsApp Us</button>
</a>
</div>
"""

# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return render_template_string(HOME)

@app.route("/shop")
def shop():
    return render_template_string(SHOP, products=products)

@app.route("/add/<int:id>")
def add(id):
    if "cart" not in session:
        session["cart"] = []
    session["cart"].append(id)
    session.modified = True
    return redirect("/shop")

@app.route("/cart")
def cart():
    items = []
    total = 0

    for cid in session.get("cart", []):
        for p in products:
            if p["id"] == cid:
                items.append(p)
                total += p["price"]

    return render_template_string(CART, items=items, total=total, upi=UPI_ID)

@app.route("/success")
def success():
    session["cart"] = []
    return render_template_string(SUCCESS)

# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)