from flask import Flask, render_template_string, request, session, redirect
import random, os

app = Flask(__name__)
app.secret_key = "casva_brand_123"

UPI_ID = "princeveguru@ibl"
BRAND = "CASVA"

# ---------------- PRODUCTS ----------------
products = [
    {"id": 1, "name": "Swarovski Beads", "price": 500},
    {"id": 2, "name": "Monalisa Beads", "price": 150},
    {"id": 3, "name": "Hydra Beads", "price": 300},
]

# ---------------- STYLE BASE ----------------
STYLE = """
<style>
body{
margin:0;
font-family:Arial;
background:url('https://images.unsplash.com/photo-1617038260897-41a1f14a8ca0') no-repeat center;
background-size:cover;
color:white;
}

.overlay{
background:rgba(0,0,0,0.75);
min-height:100vh;
padding:20px;
}

.logo{
font-size:32px;
font-weight:bold;
color:gold;
text-align:center;
padding:10px;
text-shadow:0 0 10px gold;
}

.card{
background:rgba(255,255,255,0.1);
padding:10px;
margin:10px;
border-radius:15px;
text-align:center;
box-shadow:0 0 10px cyan;
}

button{
padding:10px 15px;
margin:5px;
border:none;
border-radius:10px;
background:cyan;
font-weight:bold;
cursor:pointer;
}

button:hover{
background:gold;
}
</style>
"""

# ---------------- LOGIN ----------------
LOGIN = STYLE + """
<div class="overlay">
<div class="logo">💎 CASVA</div>

<h2 style="text-align:center">Login</h2>

<form method="POST" action="/send_otp" style="text-align:center">
<input name="mobile" placeholder="Enter Mobile Number" style="padding:10px;border-radius:8px;border:none">
<br><br>
<button>Send OTP</button>
</form>

</div>
"""

# ---------------- OTP ----------------
OTP = STYLE + """
<div class="overlay">
<div class="logo">💎 CASVA</div>

<h3 style="text-align:center">OTP sent to {{mobile}}</h3>

<form method="POST" action="/verify" style="text-align:center">
<input name="otp" placeholder="Enter OTP" style="padding:10px;border-radius:8px;border:none">
<br><br>
<button>Verify</button>
</form>

</div>
"""

# ---------------- HOME ----------------
HOME = STYLE + """
<div class="overlay">

<div class="logo">💎 CASVA</div>

<h2 style="text-align:center">Welcome to CASVA Beads</h2>
<p style="text-align:center">Premium Jewellery & Beads Brand</p>

<div style="text-align:center">
<a href="/shop"><button>Enter Shop</button></a>
<a href="/cart"><button>Cart</button></a>
</div>

</div>
"""

# ---------------- SHOP ----------------
SHOP = STYLE + """
<div class="overlay">

<div class="logo">💎 CASVA COLLECTION</div>

<div style="display:flex;flex-wrap:wrap;justify-content:center">

{% for p in products %}
<div class="card" style="width:200px">
<h3>{{p.name}}</h3>
<p>₹{{p.price}}</p>
<a href="/add/{{p.id}}"><button>Add</button></a>
</div>
{% endfor %}

</div>

<div style="text-align:center">
<a href="/cart"><button>Go to Cart</button></a>
</div>

</div>
"""

# ---------------- CART ----------------
CART = STYLE + """
<div class="overlay">

<div class="logo">💎 CASVA CART</div>

<div style="text-align:center">

{% for i in items %}
<p>{{i.name}} - ₹{{i.price}}</p>
{% endfor %}

<h3>Total: ₹{{total}}</h3>

<a href="upi://pay?pa={{upi}}&pn=CASVA&am={{total}}&cu=INR">
<button>Pay Now</button>
</a>

</div>

</div>
"""

# ---------------- ROUTES ----------------
@app.route("/")
def login():
    return render_template_string(LOGIN)

@app.route("/send_otp", methods=["POST"])
def send_otp():
    mobile = request.form["mobile"]
    otp = str(random.randint(1000,9999))
    session["otp"] = otp
    session["mobile"] = mobile
    print("OTP:", otp)
    return render_template_string(OTP, mobile=mobile)

@app.route("/verify", methods=["POST"])
def verify():
    if request.form["otp"] == session.get("otp"):
        session["logged"] = True
        return redirect("/home")
    return "Wrong OTP"

@app.route("/home")
def home():
    if not session.get("logged"):
        return redirect("/")
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

# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)