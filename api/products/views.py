from flask_restx import Resource, Namespace, fields, abort
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from ..models.products import Product
from flask import request

product_namespace = Namespace('products', description='Endpoints for managing and interacting with products in the store,\
    including creation, retrieval, updating, and deletion.')

product_model = product_namespace.model('Product', {
    "id": fields.Integer(),
    "name": fields.String(required=True, description='Product name'),
    "description": fields.String(required=True, description='Product description'),
    "quantity": fields.Integer(required=True, description='Product quantity'),
    "price": fields.Float(required=True, description='Product price'),
    "category": fields.String(required=True, description='Product category'),
})

product_status_model = product_namespace.model('Product', {
    "id": fields.Integer(),
    "name": fields.String(required=True, description='Product name'),
    "description": fields.String(required=True, description='Product description'),
    "quantity": fields.Integer(description='Product quantity'),
    "price": fields.Float(required=True, description='Product price'),
    "stock": fields.Integer(description='Product stock', default=0),
    "category": fields.String(required=True, description='Product category. Must be phone brands'),
})

pagination_model = product_namespace.model('Pagination', {
    "total": fields.Integer(description='Total number of products'),
    "pages": fields.Integer(description='Total number of pages'),
    "page": fields.Integer(description='Current page'),
    "per_page": fields.Integer(description='Number of products per page'),
    "next_page": fields.Integer(description='Next page number'),
    "prev_page": fields.Integer(description='Previous page number'),
})

product_list_model = product_namespace.model('ProductList', {
    "products": fields.List(fields.Nested(product_status_model)),
    "pagination": fields.Nested(pagination_model)
})

@product_namespace.route('/product')
class CreateAndGetAllProducts(Resource):
    @product_namespace.expect(product_model)
    @product_namespace.marshal_with(product_status_model)
    @product_namespace.doc(description="Add a new product to the store")
    @jwt_required()
    def post(self):
        """
            Adds a new phone product to the store
            Only admins can add products
            
            Returns:
                The created product
                HTTP status code:
                - 201: Created
                - 400: Bad Request
                - 403: Forbidden     
        """
        jwt_identity = get_jwt_identity()
        jwt_data = get_jwt()
        if jwt_data is None or jwt_data.get('role') != 'admin':
            product_namespace.abort(403, 'Unauthorized. Only admins can add products')
        data = product_namespace.payload
        if data.get('category') not in ['iphone', 'samsung', 'huawei', 'tecno', 
                                        'infinix', 'itel', 'nokia', 'sony', 'lg', 'htc', 
                                        'blackberry', 'motorola', 'google', 'xiaomi', 'oppo', 'vivo', 
                                        'oneplus', 'redmi', 'realme', 'lenovo']:
            product_namespace.abort(400, 'Invalid category. Category must be phone brands')
        if not data:
            product_namespace.abort(400, 'No data provided')
        product_exists = Product.query.filter_by(name=data.get('name')).first()
        if product_exists:
            product_namespace.abort(400, 'Product category already exists. Try updating the quantity instead')
            
        if not data.get('name') or not data.get('description') or not data.get('price') or not data.get('category') or not data.get('quantity'):
            product_namespace.abort(400, 'Required fields: name, description, price, category, quantity')
        if data.get('quantity') < 0:
            product_namespace.abort(400, 'Quantity must be greater than or equal to 0')
        if data.get('price') < 0:
            product_namespace.abort(400, 'Price must be greater than 0')
        if not isinstance(data.get('quantity'), int):
            product_namespace.abort(400, 'Quantity must be an integer')
        if not isinstance(data.get('price'), float):
            product_namespace.abort(400, 'Price must be a float')
        if data:
            product = Product(name=data.get('name'), description=data.get('description'), price=data.get('price'), 
                            category=data.get('category'), quantity=data.get('quantity'))
            product.stock = product.stock + product.quantity
            if not isinstance(product.stock, int):
                product_namespace.abort(400, 'Stock must be an integer')
            product.save()
            return product, 201
        return abort(500, 'Something went wrong')
    
    @product_namespace.marshal_with(product_list_model)
    @product_namespace.doc(description="Get all products in the store")
    def get(self):
        """
            Retrieve all products in the store
            Returns:
                A list of all products in the store
                HTTP status code
                 - 200: OK
                 - 400: Bad Request
                
        """
        page = request.args.get('page', default=1, type=int)
        if page < 1:
            product_namespace.abort(400, 'Page must be greater than 0')
        if not isinstance(page, int):
            product_namespace.abort(400, 'Page must be an integer')
        per_page = request.args.get('per_page', default=5, type=int)
        if per_page < 1:
            product_namespace.abort(400, 'Page must be greater than 0')
        if not isinstance(per_page, int):
            product_namespace.abort(400, 'Page must be an integer')
        products = Product.query.paginate(page=page, per_page=per_page)
        
        return {
            "products": products.items,
            "pagination": {
                "total": products.total,
                "pages": products.pages,
                "page": products.page,
                "per_page": products.per_page,
                "next_page": products.next_num,
                "prev_page": products.prev_num,
            }
        }

@product_namespace.route('/product/<int:id>')
class GetUpdateDeleteProduct(Resource):
    @product_namespace.marshal_with(product_status_model)
    @product_namespace.doc(description="Retrieve a product by its ID", params={'product_id': 'The product ID'}, 
                           required=True)
    def get(self, id):
        """
            Retrieves a specific product by its ID
            Returns:
                The product with the specified ID
                HTTP status code:
                - 200: OK
                - 404: Not Found
        """
        product = Product.query.get(id)
        if not product:
            product_namespace.abort(404, 'Product not found')
        return product, 200
    
    @product_namespace.expect(product_model)
    @product_namespace.marshal_with(product_status_model)
    @product_namespace.doc(description="Update a product by its ID",
                           params={'product_id': 'The product ID'})
    @jwt_required()
    def put(self, id):
        """
            Update a product details by its ID
            Only admins can update products
            Returns:
                The updated product
                HTTP status code:
                - 200: OK
                - 400: Bad Request
                - 403: Forbidden
                - 404: Not Found
                - 500: Internal Server Error
        """
        jwt_data = get_jwt()
        if jwt_data.get('role') != 'admin':
            product_namespace.abort(403, 'Unauthorized. Only admins can update products')
        product = Product.query.get(id)
        if not product:
            product_namespace.abort(404, 'Product not found')
        data = product_namespace.payload
        if not data:
            product_namespace.abort(400, 'No data provided')
        if not isinstance(data.get('quantity'), int):
            product_namespace.abort(400, 'Quantity must be an integer')
        if not isinstance(data.get('price'), float):
            product_namespace.abort(400, 'Price must be a float')
        if data.get('price') and data.get('price') < 0:
            product_namespace.abort(400, 'Price cannot be negative')
        if data.get('quantity') and data.get('quantity') < 0:
            product_namespace.abort(400, 'Quantity cannot be negative')
        if data.get('category') and data.get('category') not in ['iphone', 'samsung', 'huawei', 'tecno', 
                                        'infinix', 'itel', 'nokia', 'sony', 'lg', 'htc', 
                                        'blackberry', 'motorola', 'google', 'xiaomi', 'oppo', 'vivo', 
                                        'oneplus', 'redmi', 'realme', 'lenovo']:
            product_namespace.abort(400, 'Invalid category. Category must be phone brands')
        
        # Update only the fields that are actually provided in the payload
        if data.get('name'):
            product.name = data.get('name')
        if data.get('description'):
            product.description = data.get('description')
        if data.get('price'):
            product.price = data.get('price')
        if data.get('category'):
            product.category = data.get('category')
        if data.get('quantity'):
            # Update the stock only when the quantity is updated
            product.quantity = data.get('quantity')
            product.stock = product.stock + product.quantity
        try:
            product.save()
            return product, 200
        except Exception as e:
            product_namespace.abort(500, 'Failed to update product')


    
    @product_namespace.marshal_with(product_status_model)
    @product_namespace.doc(description="Delete a product by its ID",
                           params={'product_id': 'The product ID'},
                           )
    @jwt_required()
    def delete(self, id):
        """
            Deletes a specific product by its ID
            Only admins can delete products
            Returns:
                A success message upon successful deletion
                HTTP status code:
                - 200: OK
                - 403: Forbidden
                - 404: Not Found
        """
        jwt_data = get_jwt()
        if jwt_data.get('role') != 'admin':
            product_namespace.abort(403, 'Unauthorized. Only admins can delete products')
        product = Product.query.get(id)
        if not product:
            product_namespace.abort(404, 'Product not found')
        product.delete()
        return {"message": "Product deleted successfully"}, 200
    
    
    