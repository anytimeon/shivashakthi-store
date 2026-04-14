from flask import Flask, render_template_string, redirect, url_for, session, request

app = Flask(__name__)
app.secret_key = "shivashakthi123"

UPI_ID = "princeveguru@ibl"

# ---------------- PRODUCTS ----------------
products = [
    {"id": 1, "name": "Swarovski Round Beads", "price": 500},
    {"id": 2, "name": "Monalisa Beads", "price": 150},
    {"id": 3, "name": "Hydra Beads", "price": 300},
    {"id": 4, "name": "Pearl Beads", "price": 200}
]

# ---------------- HOME ----------------
HOME = """
<h1 style='text-align:center'>🛕 Shiva Shakthi Beads Store</h1>
<div style='text-align:center'>
<a href='/products'><button>Products</button></a>
<a href='/cart'><button>Cart</button></a>
<a href='/wallet'><button>Wallet Top-Up</button></a>
</div>
"""

# ---------------- PRODUCTS PAGE ----------------
PRODUCTS = """
<h2 style='text-align:center'>📿 Beads Collection</h2>
<div style='text-align:center'>
{% for p in products %}
<div style='border:1px solid #ccc;margin:10px;padding:10px'>
<h3>{{p.name}}</h3>
<p>₹{{p.price}}</p>
<a href='/add/{{p.id}}'><button>Add to Cart</button></a>
</div>
{% endfor %}
</div>
<a href='/cart'><button>Go to Cart</button></a>
"""

# ---------------- CART PAGE ----------------
CART = """
<h2 style='text-align:center'>🛒 Your Cart</h2>

<div style='text-align:center'>
{% for item in items %}
<p>{{item.name}} - ₹{{item.price}}</p>
<a href='/remove/{{item.id}}'>Remove</a>
<br>
{% endfor %}

<h3>Total: ₹{{total}}</h3>

<a href="upi://pay?pa={{upi}}&pn=Shiva%20Shakthi&am={{total}}&cu=INR">
<button>Pay with UPI</button>
</a>
</div>
"""

# ---------------- WALLET ----------------
WALLET = """
<h2 style='text-align:center'>💰 Wallet Top-Up</h2>

<form action="/pay" style="text-align:center">
<input type="number" name="amount" placeholder="Enter amount ₹" required>
<br><br>
<button type="submit">Continue</button>
</form>

{% if amount %}
<div style="text-align:center">
<br>
<a href="upi://pay?pa={{upi}}&pn=Shiva%20Shakthi&am={{amount}}&cu=INR">
<button>Open UPI ₹{{amount}}</button>
</a>
</div>
{% endif %}
"""

# ---------------- ROUTES ----------------

@app.route("/")
def home():
    return render_template_string(HOME)

@app.route("/products")
def show_products():
    return render_template_string(PRODUCTS, products=products)

@app.route("/add/<int:id>")
def add(id):
    if "cart" not in session:
        session["cart"] = []
    session["cart"].append(id)
    session.modified = True
    return redirect(url_for("show_products"))

@app.route("/remove/<int:id>")
def remove(id):
    if "cart" in session and id in session["cart"]:
        session["cart"].remove(id)
        session.modified = True
    return redirect(url_for("cart"))

@app.route("/cart")
def cart():
    if "cart" not in session:
        session["cart"] = []

    items = []
    total = 0

    for cid in session["cart"]:
        for p in products:
            if p["id"] == cid:
                items.append(p)
                total += p["price"]

    return render_template_string(CART, items=items, total=total, upi=UPI_ID)

@app.route("/wallet")
def wallet():
    return render_template_string(WALLET, amount=None, upi=UPI_ID)

@app.route("/pay")
def pay():
    amount = request.args.get("amount")
    return render_template_string(WALLET, amount=amount, upi=UPI_ID)

# ---------------- RUN ----------------
app.run(host="0.0.0.0", port=5000)