from flask import Flask, jsonify
from datetime import datetime, timedelta
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
db = SQLAlchemy(app)

# Define models
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    sku = db.Column(db.String(50))
    company_id = db.Column(db.Integer)

class Sales(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)

class ProductThreshold(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    low_stock_threshold = db.Column(db.Integer)

class Warehouse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    company_id = db.Column(db.Integer)

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse.id'))
    quantity = db.Column(db.Integer)

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    contact_email = db.Column(db.String(100))

class ProductSupplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))

@app.route('/api/companies/<int:company_id>/alerts/low-stock', methods=['GET'])
def get_low_stock_alerts(company_id):
    try:
        alerts = []

        # Define recent activity window
        last_30_days = datetime.utcnow() - timedelta(days=30)

        # Step 1: Get all products for the company
        products = Product.query.filter_by(company_id=company_id).all()

        for product in products:
            # Step 2: Check recent sales
            recent_sales = db.session.query(
                func.sum(Sales.quantity).label('total_sold'),
                func.count(Sales.id).label('days_count')
            ).filter(
                Sales.product_id == product.id,
                Sales.created_at >= last_30_days
            ).first()

            if not recent_sales or not recent_sales.total_sold:
                continue  # skip products with no recent sales

            avg_daily_sales = recent_sales.total_sold / 30

            # Step 3: Get threshold
            threshold_entry = ProductThreshold.query.filter_by(product_id=product.id).first()
            threshold = threshold_entry.low_stock_threshold if threshold_entry else 10

            # Step 4: Get inventory across warehouses
            inventories = db.session.query(Inventory, Warehouse).join(
                Warehouse, Inventory.warehouse_id == Warehouse.id
            ).filter(
                Inventory.product_id == product.id,
                Warehouse.company_id == company_id
            ).all()

            for inv, warehouse in inventories:
                current_stock = inv.quantity

                # Step 5: Check low stock condition
                if current_stock < threshold:
                    # Step 6: Calculate days until stockout
                    days_until_stockout = int(current_stock / avg_daily_sales) if avg_daily_sales > 0 else None

                    # Step 7: Get supplier
                    supplier = db.session.query(Supplier).join(
                        ProductSupplier,
                        Supplier.id == ProductSupplier.supplier_id
                    ).filter(
                        ProductSupplier.product_id == product.id
                    ).first()

                    alerts.append({
                        "product_id": product.id,
                        "product_name": product.name,
                        "sku": product.sku,
                        "warehouse_id": warehouse.id,
                        "warehouse_name": warehouse.name,
                        "current_stock": current_stock,
                        "threshold": threshold,
                        "days_until_stockout": days_until_stockout,
                        "supplier": {
                            "id": supplier.id if supplier else None,
                            "name": supplier.name if supplier else None,
                            "contact_email": supplier.contact_email if supplier else None
                        }
                    })

        return jsonify({
            "alerts": alerts,
            "total_alerts": len(alerts)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
