def test_get_products_returns_empty_list(client):
    response = client.get("/products")
    assert response.status_code == 200
    assert response.get_json() == []

def test_create_product_success(client):
    new_product = {
        "name": "Test product",
        "price": 19.99
    }

    response = client.post('/products', json=new_product)
    assert response.status_code == 201
    product = response.get_json()
    assert 'id' in product
    assert product['name'] == "Test product"

def test_get_products_success(client):
    response = client.get('/products')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)