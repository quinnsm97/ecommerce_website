from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

app = Flask(__name__)

#                                      database+driver://username:password@server:port/databasename

app.config['SQLALCHEMY_DATABASE_URI']="postgresql+psycopg2://mar_user:123456@localhost:5432/mar_ecommerce"

db = SQLAlchemy(app)
ma = Marshmallow(app)

class Product(db.Model):
    # Define table name
    __tablename__ = "products"
    # Define primary key
    id = db.Column(db.Integer, primary_key=True)
    # Define non-key attributes
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    price = db.Column(db.Float)
    stock = db.Column(db.Integer)

    def __init__(self, name, description, price, stock):
        self.name = name
        self.description = description
        self.price = price
        self.stock = stock


# Create a class for ProductSchema
class ProductSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        load_instance = True

# ProductSchema instance to handle multiple products
products_schema = ProductSchema(many=True)

# ProductSchema instance to handle single product
product_schema = ProductSchema()

@app.cli.command("create") # flask create
def create_table():
    db.create_all()
    print("Tables created!")

@app.cli.command("drop") # flask drop
def drop_tables():
    db.drop_all()
    print("Tables dropped!")

@app.cli.command("seed") # flask seed
def seed_tables():
    # Create an instance of products
    product1 = Product(
        name = "Product 1",
        description = "This is Product 1",
        price = 12.99,
        stock = 5
    )

    product2 = Product(
        name = "Product 2",
        description = "This is Product 2",
        price = 13,
        stock = 0
    )

    # Like Git operations, we need to add and commit
    db.session.add(product1)
    db.session.add(product2)
    
    db.session.commit()

    print("Table seeded successfully.")

# CRUD Operations on the Products Table
# GET, POST, PUT, PATCH, DELETE
# READ Operation - GET method
# GET /products
@app.route("/products")
def get_products():
    # Statement: SELECT * FROM products;
    products_list = Product.query.all()

    # Convert the object to JSON format - Serialise
    data = products_schema.dump(products_list)
    return jsonify(data)

# READ specific product from the products list
# GET /products/id
@app.route("/products/<int:product_id>")
def get_a_product(product_id):
    # Statement: SELECT * FROM products WHERE id=product_id;
    product = Product.query.get(product_id)

    if product:
        data = product_schema.dump(product)
        return jsonify(data)
    else:
        return jsonify({"message": f"Product with id {product_id} does not exist."}), 404

# CREATE a product
# POST /products
@app.route("/products", methods=["POST"])
def create_product():
    # Statement: INSERT INTO products(arg1, arg2, ..) VALUES (value1, value2, ..)
    # Get the body JSON data
    body_data = request.get_json()
    # Create a Product object and pass on the values
    new_product = Product(
        name = body_data.get("name"),
        description = body_data.get("description"),
        price = body_data.get("price"),
        stock = body_data.get("stock")
    )
    # Add to the session and commit
    db.session.add(new_product)
    db.session.commit()

    # Return the newly created product
    data = product_schema.dump(new_product)
    return jsonify(data), 201

# DELETE a product
# DELETE /products/id
@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    # Statement: DELETE * FROM products WHERE id=product_id;
    # Find the product with the product_id from the database
    # Statement: SELECT * FROM products WHERE id = product_id;
    # Method 1:
    # stmt = db.select(Product).filter_by(id=product_id)
    # product = db.session.scalar(stmt)
    # Method 2:
    product = Product.query.get(product_id)
    # if it exists
    if product:
        # delete the product
        db.session.delete(product)
        db.session.commit()
        # send an acknowledgement message
        return {"message": f"Product with id {product_id} deleted successfully."}
    # else
    else:
        # send an acknowledgement message
        return {"message": f"Product with id {product_id} does not exist."}
    
# UPDATE method: PUT, PATCH
# PUT/PATCH /products/id
@app.route("/products/<int:product_id>", methods=["PUT", "PATCH"])
def update_product(product_id):
    # Statement: UPDATE products SET column_name=value;
    # Find the product with the id = product_id
    product = Product.query.get(product_id)
    # if product exists
    if product:
        # Fetch the updated values from the request body
        body_data = request.get_json()
        # Update the values - SHORT CIRCUIT
        # product.name = body_data.get("name") or product.name
        # product.description = body_data.get("description") or product.description
        # product.price = body_data.get("price") or product.price
        # product.stock = body_data.get("stock") or product.stock

        product.name = body_data.get("name", product.name)
        product.description = body_data.get("description", product.description)
        product.price = body_data.get("price", product.price)
        product.stock = body_data.get("stock", product.stock)        

        db.session.commit()
        # acknowledgement message
        return jsonify(product_schema.dump(product))
    # else
    else:
        # acknowledgement message
        return {"message": f"Product with id {product_id} does not exist."}, 404
