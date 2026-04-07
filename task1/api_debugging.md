from decimal import Decimal
from flask import request, jsonify
from sqlalchemy.exc import IntegrityError

@app.route('/api/products', methods=['POST'])
def create_product():
   try:
       data = request.get_json()

       # Validate required fields
       required_fields = ['name', 'sku', 'price']
       for field in required_fields:
           if field not in data:
               return jsonify({"error": f"{field} is required"}), 400

       # Validate price
       try:
           price = Decimal(str(data['price']))
           if price < 0:
               return jsonify({"error": "Price cannot be negative"}), 400
       except:
           return jsonify({"error": "Invalid price format"}), 400

       # Check SKU uniqueness
       existing_product = Product.query.filter_by(sku=data['sku']).first()
       if existing_product:
           return jsonify({"error": "SKU already exists"}), 400

       # Create product (not tied to a single warehouse)
       product = Product(
           name=data['name'],
           sku=data['sku'],
           price=price
       )

       db.session.add(product)
       db.session.flush()

       # Optional inventory creation
       if 'warehouse_id' in data and 'initial_quantity' in data:
           quantity = data.get('initial_quantity', 0)

           if quantity < 0:
               return jsonify({"error": "Quantity cannot be negative"}), 400

           inventory = Inventory(
               product_id=product.id,
               warehouse_id=data['warehouse_id'],
               quantity=quantity
           )
           db.session.add(inventory)

       # Single commit
       db.session.commit()

       return jsonify({
           "message": "Product created successfully",
           "product_id": product.id
       }), 201

   except IntegrityError:
       db.session.rollback()
       return jsonify({"error": "Database integrity error"}), 400

   except Exception as e:
       db.session.rollback()
       return jsonify({"error": str(e)}), 500