import os
import re
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "mrmobile_ultra_ecommerce_2026"

UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

ADMIN_PASSWORD = "admin"
SHOP_UPI_ID = "mrmobile@upi"  # আপনার আসল UPI ID এখানে বসাবেন

# ডাইনামিক স্লাইডার ব্যানার (যার মধ্যে শোরুম অফারও ঘুরবে)
banners = [
    {
        "id": 1,
        "title": "Mister Mobile Now at Gidhni, Jhargram, Silda",
        "subtitle": "আপনার নিকটস্থ শাখায় এসে আজই আসল ব্র্যান্ড ওয়ারেন্টি সহ ফোন সংগ্রহ করুন!",
        "image": "https://images.unsplash.com/photo-1556742049-0a67c5574f73?w=1200&q=80",
        "badge": "🏬 Official Stores"
    },
    {
        "id": 2,
        "title": "Mega Mobile Festival 2026",
        "subtitle": "শীর্ষ ব্র্যান্ডের স্মার্টফোনে ধামাকা ক্যাশব্যাক ও এক্সচেঞ্জ অফার!",
        "image": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=1200&q=80",
        "badge": "⚡ Limited Time Deal"
    }
]

# একাধিক ছবি সহ ফোনের তালিকা
phones = [
    {
        "id": 1,
        "name": "Samsung Galaxy S24 Ultra 5G",
        "brand": "Samsung",
        "ram_rom": "12 GB RAM | 256 GB Storage",
        "price": 129999,
        "original_price": 134999,
        "discount": "4% off",
        "stock": 5,
        "rating": 4.7,
        "description": "Snapdragon 8 Gen 3 প্রসেসর, 200MP কোয়াড ক্যামেরা সেটআপ, 5000mAh দীর্ঘস্থায়ী ব্যাটারি এবং টাইটানিয়াম ফ্রেম।",
        "images": [
            "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=700&q=80",
            "https://images.unsplash.com/photo-1580910051074-3eb694886505?w=700&q=80",
            "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=700&q=80"
        ],
        "reviews": [
            {"user": "Sourav", "comment": "অসাধারণ ক্যামেরা কোয়ালিটি এবং ব্যাটারি ব্যাকআপ দারুণ!", "stars": 5}
        ]
    },
    {
        "id": 2,
        "name": "Apple iPhone 15 Pro",
        "brand": "Apple",
        "ram_rom": "8 GB RAM | 128 GB Storage",
        "price": 127990,
        "original_price": 134900,
        "discount": "5% off",
        "stock": 3,
        "rating": 4.8,
        "description": "A17 Pro চিপসেট, অ্যাকশন বাটন, সুপার রেটিনা XDR ডিসপ্লে এবং স্টুডিও গ্রেড প্রো ক্যামেরা সিস্টেম।",
        "images": [
            "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=700&q=80",
            "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=700&q=80"
        ],
        "reviews": [
            {"user": "Pooja", "comment": "ন্যাচারাল টাইটানিয়াম ফিনিশ অসাধারণ!", "stars": 5}
        ]
    },
    {
        "id": 3,
        "name": "Redmi Note 13 Pro+ 5G",
        "brand": "Redmi",
        "ram_rom": "8 GB RAM | 256 GB Storage",
        "price": 26999,
        "original_price": 33999,
        "discount": "20% off",
        "stock": 10,
        "rating": 4.4,
        "description": "120W হাইপারচার্জ, 200MP OIS ক্যামেরা, কার্ভড AMOLED ডিসপ্লে এবং IP68 ওয়াটার রেজিস্ট্যান্স।",
        "images": [
            "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=700&q=80",
            "https://images.unsplash.com/photo-1580910051074-3eb694886505?w=700&q=80"
        ],
        "reviews": [
            {"user": "Rahul", "comment": "বাজেটের মধ্যে সেরা অল-রাউন্ডার ফোন!", "stars": 4}
        ]
    }
]

orders = []

def parse_budget_query(query):
    pattern = r'under\s*(\d+)\s*(k)?'
    match = re.search(pattern, query.lower())
    if match:
        val = int(match.group(1))
        if match.group(2) == 'k':
            val *= 1000
        return val
    return None

@app.route('/')
def home():
    query = request.args.get('search', '').strip()
    cart_count = len(session.get('cart', []))
    
    filtered_phones = phones
    if query:
        budget = parse_budget_query(query)
        if budget is not None:
            filtered_phones = [p for p in phones if p['price'] <= budget]
        else:
            q_lower = query.lower()
            filtered_phones = [
                p for p in phones 
                if q_lower in p['name'].lower() 
                or q_lower in p['ram_rom'].lower() 
                or q_lower in p.get('brand', '').lower()
            ]

    return render_template('index.html', phones=filtered_phones, banners=banners, query=query, cart_count=cart_count)

# প্রোডাক্ট ডিটেইলস পেজ (একাধিক ছবি ও রিকমেন্ডেশন সহ)
@app.route('/product/<int:phone_id>')
def product_detail(phone_id):
    selected_phone = next((p for p in phones if p["id"] == phone_id), None)
    if not selected_phone:
        return "ফোনটি পাওয়া যায়নি!", 404
    
    # নিচে দেখানোর জন্য অন্যান্য সমস্ত ফোন
    more_phones = [p for p in phones if p["id"] != phone_id]
    cart_count = len(session.get('cart', []))
    return render_template('product_detail.html', phone=selected_phone, more_phones=more_phones, cart_count=cart_count)

# রিভিউ সাবমিট
@app.route('/product/<int:phone_id>/review', methods=['POST'])
def add_review(phone_id):
    selected_phone = next((p for p in phones if p["id"] == phone_id), None)
    if selected_phone:
        user_name = request.form.get('user', 'Customer')
        comment = request.form.get('comment', '')
        stars = int(request.form.get('stars', 5))
        selected_phone['reviews'].append({"user": user_name, "comment": comment, "stars": stars})
    return redirect(url_for('product_detail', phone_id=phone_id))

# কার্ট সিস্টেম
@app.route('/cart/add/<int:phone_id>')
def add_to_cart(phone_id):
    cart = session.get('cart', [])
    if phone_id not in cart:
        cart.append(phone_id)
        session['cart'] = cart
    return redirect(url_for('cart_view'))

@app.route('/cart')
def cart_view():
    cart_ids = session.get('cart', [])
    cart_items = [p for p in phones if p['id'] in cart_ids]
    total_amount = sum(item['price'] for item in cart_items)
    return render_template('cart.html', items=cart_items, total=total_amount)

@app.route('/cart/remove/<int:phone_id>')
def remove_from_cart(phone_id):
    cart = session.get('cart', [])
    if phone_id in cart:
        cart.remove(phone_id)
        session['cart'] = cart
    return redirect(url_for('cart_view'))

# বাই নাও পেজ
@app.route('/buy/<int:phone_id>', methods=['GET', 'POST'])
def buy(phone_id):
    selected_phone = next((p for p in phones if p["id"] == phone_id), None)
    if not selected_phone:
        return "মোবাইলটি পাওয়া যায়নি!", 404

    total_price = float(selected_phone["price"])
    advance_20 = round(total_price * 0.20, 2)
    due_80 = round(total_price - advance_20, 2)

    upi_payment_link = f"upi://pay?pa={SHOP_UPI_ID}&pn=MR.Mobile&am={advance_20}&cu=INR&tn=Booking_{selected_phone['id']}"
    qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=230x230&data={upi_payment_link}"

    saved_name = session.get('customer_name', '')
    saved_phone = session.get('customer_phone', '')
    saved_address = session.get('customer_address', '')

    if request.method == 'POST':
        if selected_phone["stock"] <= 0:
            return "<script>alert('দুঃখিত! এই মডেলটির স্টক বর্তমানে শেষ।'); window.location.href='/';</script>"

        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        txn_id = request.form.get('txn_id', 'N/A')

        session['customer_name'] = name
        session['customer_phone'] = phone
        session['customer_address'] = address

        # স্ক্রিনশট আপলোড
        screenshot_file = request.files.get('screenshot')
        screenshot_url = None
        if screenshot_file and allowed_file(screenshot_file.filename):
            s_name = secure_filename(f"pay_{len(orders)+1}_{screenshot_file.filename}")
            screenshot_file.save(os.path.join(app.config['UPLOAD_FOLDER'], s_name))
            screenshot_url = url_for('static', filename=f"uploads/{s_name}")

        selected_phone["stock"] -= 1

        new_order = {
            "order_id": len(orders) + 1,
            "phone_name": selected_phone["name"],
            "phone_image": selected_phone["images"][0],
            "total_price": total_price,
            "advance_paid": advance_20,
            "due_amount": due_80,
            "customer_name": name,
            "customer_phone": phone,
            "address": address,
            "txn_id": txn_id,
            "screenshot": screenshot_url,
            "status": "Order Placed",  # Order Placed -> Verified & Accepted -> Out for Delivery -> Delivered
            "bill_url": None           # অ্যাডমিন বিল আপলোড করলে এখানে লিংক সেভ হবে
        }
        orders.append(new_order)
        return render_template('order_success.html', order=new_order)

    return render_template('buy.html', 
                           phone=selected_phone, 
                           advance_20=advance_20, 
                           due_80=due_80, 
                           qr_url=qr_code_url, 
                           shop_upi=SHOP_UPI_ID,
                           saved_name=saved_name,
                           saved_phone=saved_phone,
                           saved_address=saved_address)

# কাস্টমারদের "My Orders" ট্র্যাকিং পেজ
@app.route('/my-orders')
def my_orders():
    user_phone = request.args.get('phone') or session.get('customer_phone', '')
    user_orders = []
    if user_phone:
        user_orders = [o for o in orders if str(o['customer_phone']).strip() == str(user_phone).strip()]
    return render_template('my_orders.html', orders=user_orders, phone=user_phone)

# অ্যাডমিন প্যানেল
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        # অ্যাডমিন লগইন
        if 'login_btn' in request.form:
            if request.form.get('password') == ADMIN_PASSWORD:
                session['admin_logged_in'] = True
                return redirect(url_for('admin'))
            else:
                return "<script>alert('ভুল পাসওয়ার্ড!'); window.location.href='/admin';</script>"

        # ১. নতুন ফোন অ্যাড (একাধিক ছবি ও অটো ডিসকাউন্ট সহ)
        if 'add_phone' in request.form and session.get('admin_logged_in'):
            name = request.form.get('name')
            brand = request.form.get('brand', 'Smartphone')
            ram_rom = request.form.get('ram_rom')
            price = float(request.form.get('price'))
            orig_price = float(request.form.get('original_price') or price)
            stock = int(request.form.get('stock') or 1)
            desc = request.form.get('description', '')

            # ডিসকাউন্ট পার্সেন্টেজ হিসাব
            if orig_price > price:
                disc_pct = round(((orig_price - price) / orig_price) * 100)
                discount = f"{disc_pct}% off"
            else:
                discount = "Special Deal"

            # একাধিক ছবি আপলোড
            uploaded_images = []
            files = request.files.getlist('phone_files')
            for f in files:
                if f and allowed_file(f.filename):
                    fname = secure_filename(f"p_{len(phones)+1}_{f.filename}")
                    f.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
                    uploaded_images.append(url_for('static', filename=f"uploads/{fname}"))

            if not uploaded_images:
                uploaded_images = ["https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=700&q=80"]

            phones.append({
                "id": len(phones) + 1,
                "name": name,
                "brand": brand,
                "ram_rom": ram_rom,
                "price": price,
                "original_price": orig_price,
                "discount": discount,
                "stock": stock,
                "rating": 4.6,
                "description": desc,
                "images": uploaded_images,
                "reviews": []
            })
            return redirect(url_for('admin'))

        # ২. পুরোনো ফোনের দাম ও স্টক এডিট করা
        if 'edit_phone_price' in request.form and session.get('admin_logged_in'):
            pid = int(request.form.get('phone_id'))
            new_price = float(request.form.get('new_price'))
            new_orig = float(request.form.get('new_original_price'))
            new_stock = int(request.form.get('new_stock'))

            for p in phones:
                if p["id"] == pid:
                    p["price"] = new_price
                    p["original_price"] = new_orig
                    p["stock"] = max(0, new_stock)
                    if new_orig > new_price:
                        disc_pct = round(((new_orig - new_price) / new_orig) * 100)
                        p["discount"] = f"{disc_pct}% off"
                    else:
                        p["discount"] = "Best Deal"
                    break
            return redirect(url_for('admin'))

        # ৩. নতুন ব্যানার অ্যাড (কম্পিউটার থেকে ছবি আপলোড)
        if 'add_banner' in request.form and session.get('admin_logged_in'):
            title = request.form.get('title')
            subtitle = request.form.get('subtitle')
            badge = request.form.get('badge') or "Special Deal"
            img_url = "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=1200&q=80"

            b_file = request.files.get('banner_file')
            if b_file and allowed_file(b_file.filename):
                fname = secure_filename(f"ban_{len(banners)+1}_{b_file.filename}")
                b_file.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
                img_url = url_for('static', filename=f"uploads/{fname}")

            banners.append({
                "id": len(banners) + 1,
                "title": title,
                "subtitle": subtitle,
                "image": img_url,
                "badge": badge
            })
            return redirect(url_for('admin'))

        # ৪. বিলে ফাইল আপলোড ও স্ট্যাটাস আপডেট
        if 'upload_bill' in request.form and session.get('admin_logged_in'):
            oid = int(request.form.get('order_id'))
            bill_file = request.files.get('bill_file')
            status = request.form.get('status')

            for o in orders:
                if o["order_id"] == oid:
                    if bill_file and allowed_file(bill_file.filename):
                        fname = secure_filename(f"bill_{oid}_{bill_file.filename}")
                        bill_file.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
                        o["bill_url"] = url_for('static', filename=f"uploads/{fname}")
                    if status:
                        o["status"] = status
                    break
            return redirect(url_for('admin'))

    if session.get('admin_logged_in'):
        return render_template('admin.html', phones=phones, orders=orders, banners=banners)

    # লগইন পেজ (ফাঁকা ফিল্ড)
    return """
    <!DOCTYPE html>
    <html lang="bn"><head><meta charset="UTF-8"><title>MR.Mobile Admin Login</title><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
    <body style="background:#f1f3f6; font-family:Arial, sans-serif; display:flex; justify-content:center; align-items:center; height:100vh; margin:0;">
        <div style="background:#fff; padding:35px 30px; border-radius:6px; box-shadow:0 3px 12px rgba(0,0,0,0.15); width:320px; text-align:center;">
            <h2 style="color:#2874f0; margin:0 0 10px;">MR.Mobile Admin</h2>
            <p style="color:#777; font-size:13px; margin-bottom:20px;">দোকানের কন্ট্রোল প্যানেলে লগইন করুন</p>
            <form method="POST">
                <input type="password" name="password" style="width:100%; box-sizing:border-box; padding:11px; border:1px solid #ccc; border-radius:3px; margin-bottom:15px; font-size:15px;" required autocomplete="off">
                <button type="submit" name="login_btn" style="width:100%; background:#fb641b; color:#fff; border:none; padding:12px; font-weight:bold; border-radius:3px; cursor:pointer;">LOGIN</button>
            </form>
        </div>
    </body></html>
    """

# ব্যানার ডিলিট
@app.route('/admin/banner/delete/<int:banner_id>')
def delete_banner(banner_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))
    global banners
    banners = [b for b in banners if b["id"] != banner_id]
    return redirect(url_for('admin'))

# অর্ডার অ্যাকসেপ্ট ও ডিলিট
@app.route('/admin/order/accept/<int:order_id>')
def accept_order(order_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))
    for o in orders:
        if o["order_id"] == order_id:
            o["status"] = "Verified & Accepted"
            break
    return redirect(url_for('admin'))

@app.route('/admin/order/delete/<int:order_id>')
def delete_order(order_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))
    global orders
    orders = [o for o in orders if o["order_id"] != order_id]
    return redirect(url_for('admin'))

@app.route('/admin/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)