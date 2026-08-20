"""Deterministic medicine catalog and commerce helpers for MediMind."""

from copy import deepcopy


_MEDICINE_TEMPLATES = [
    ("Paracetamol", "Painkiller", "Relief of mild pain and fever", 120, "Getz Pharma"),
    ("Ibuprofen", "Painkiller", "Relief of pain, inflammation, and fever", 180, "Abbott"),
    ("Amoxicillin", "Antibiotic", "Prescription antibiotic for bacterial infections", 260, "Sami Pharmaceuticals"),
    ("Azithromycin", "Antibiotic", "Prescription antibiotic for selected bacterial infections", 350, "Hilton Pharma"),
    ("Cetirizine", "Allergy", "Relief of allergy symptoms and sneezing", 95, "GSK Pakistan"),
    ("Omeprazole", "Digestive health", "Reduces stomach acid and heartburn symptoms", 150, "The Searle Company"),
    ("ORS Sachet", "Hydration", "Helps replace fluids and electrolytes", 35, "Unisa Pakistan"),
    ("Vitamin C", "Vitamin", "Daily vitamin C supplement", 220, "Nutrifactor"),
    ("Calcium D", "Vitamin", "Calcium and vitamin D supplement for bone health", 420, "Atco Laboratories"),
    ("Multivitamin", "Vitamin", "Broad daily vitamin and mineral supplement", 550, "Herbion"),
    ("Loratadine", "Allergy", "Non-drowsy relief for seasonal allergies", 140, "Martin Dow"),
    ("Antacid Suspension", "Digestive health", "Temporary relief from acidity and indigestion", 130, "Sami Pharmaceuticals"),
    ("Cough Relief Syrup", "Cold and cough", "Soothes cough and throat irritation", 240, "AGP Limited"),
    ("Saline Nasal Spray", "Cold and cough", "Moisturizes and clears a dry or blocked nose", 190, "Ferozsons Laboratories"),
    ("Zinc Supplement", "Vitamin", "Zinc supplement for daily nutritional support", 300, "Nutrifactor"),
    ("Diclofenac Gel", "Painkiller", "Topical relief for localized muscle and joint pain", 275, "Hilton Pharma"),
    ("Mupirocin Ointment", "Skin care", "Topical antibiotic for minor bacterial skin infections", 325, "GSK Pakistan"),
    ("Hydrocortisone Cream", "Skin care", "Short-term relief from mild skin irritation and itching", 180, "The Searle Company"),
    ("Artificial Tears", "Eye care", "Lubricating drops for dry or tired eyes", 290, "Sami Pharmaceuticals"),
    ("Iron Supplement", "Vitamin", "Iron and folic acid nutritional supplement", 390, "Atco Laboratories"),
]


def _build_catalog():
    catalog = []
    for template_index, (name, category, description, price, manufacturer) in enumerate(_MEDICINE_TEMPLATES):
        for pack_number in range(1, 11):
            catalog.append(
                {
                    "id": f"MED-{template_index + 1:02d}-{pack_number:02d}",
                    "name": f"{name} {pack_number * 10} pack",
                    "category": category,
                    "description": description,
                    "price_pkr": price + (pack_number - 1) * 12,
                    "stock": 18 + ((template_index * 7 + pack_number * 3) % 83),
                    "manufacturer": manufacturer,
                }
            )
    return catalog


MEDICINES = _build_catalog()


def get_catalog():
    """Return a session-safe copy of the 200-item catalog."""
    return deepcopy(MEDICINES)


def search_medicines(catalog, query="", category="All"):
    query = query.strip().lower()
    symptom_category = _category_for_request(query)
    return [
        medicine
        for medicine in catalog
        if (category == "All" or medicine["category"] == category)
        and (
            not query
            or query in " ".join(str(value).lower() for value in medicine.values())
            or medicine["category"] == symptom_category
        )
    ]


def _category_for_request(request):
    keyword_categories = {
        "headache": "Painkiller",
        "pain": "Painkiller",
        "fever": "Painkiller",
        "allerg": "Allergy",
        "sneeze": "Allergy",
        "heartburn": "Digestive health",
        "acidity": "Digestive health",
        "cough": "Cold and cough",
        "cold": "Cold and cough",
        "vitamin": "Vitamin",
        "bone": "Vitamin",
        "dehydrat": "Hydration",
    }
    return next((value for key, value in keyword_categories.items() if key in request), None)


def recommend_medicines(catalog, request):
    """Recommend catalog items from symptom keywords, without diagnosing."""
    category = _category_for_request(request.lower())
    if category is None:
        return []
    return [medicine for medicine in catalog if medicine["category"] == category and medicine["stock"] > 0][:3]


def add_to_cart(cart, medicine_id, quantity, catalog):
    medicine = next((item for item in catalog if item["id"] == medicine_id), None)
    if medicine is None:
        return False, "Medicine not found."
    if quantity < 1 or quantity > medicine["stock"]:
        return False, f"Choose a quantity from 1 to {medicine['stock']}."
    cart[medicine_id] = cart.get(medicine_id, 0) + quantity
    return True, f"Added {quantity} x {medicine['name']} to your cart."


def cart_items(cart, catalog):
    items = []
    for medicine_id, quantity in cart.items():
        medicine = next((item for item in catalog if item["id"] == medicine_id), None)
        if medicine:
            items.append({**medicine, "quantity": quantity, "total_pkr": quantity * medicine["price_pkr"]})
    return items


def cart_total(cart, catalog):
    return sum(item["total_pkr"] for item in cart_items(cart, catalog))


def checkout(cart, catalog):
    items = cart_items(cart, catalog)
    if not items:
        return False, "Your cart is empty.", None
    for item in items:
        medicine = next(medicine for medicine in catalog if medicine["id"] == item["id"])
        if item["quantity"] > medicine["stock"]:
            return False, f"Not enough stock for {medicine['name']}.", None
    for item in items:
        medicine = next(medicine for medicine in catalog if medicine["id"] == item["id"])
        medicine["stock"] -= item["quantity"]
    order = {"items": items, "total_pkr": sum(item["total_pkr"] for item in items)}
    cart.clear()
    return True, "Order confirmed.", order