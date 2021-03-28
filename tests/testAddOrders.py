import requests


class TestAddOrders:
    URL = 'http://127.0.0.1:8080/orders'
    JSON = {'data': [{'order_id': 1,
                      'weight': 10.00,
                      'region': 1,
                      'delivery_hours': ['09:00-21:00', ]}]}

    def test_correct_order(self):
        response = requests.post(self.URL, json=self.JSON)
        assert response.json() == {"orders": [{"id": 1}, ]}
        assert response.status_code == 201

    def test_incorrect_id(self):
        response = requests.post(self.URL, json=self.JSON)
        assert response.json() == {"validation_error": {'orders': [{"id": 1}, ]}}
        assert response.status_code == 400

    def test_incorrect_weight_type(self):
        json = self.JSON
        json['data'][0]['order_id'] = 2
        json['data'][0]['weight'] = '10.00'
        response = requests.post(self.URL, json=json)
        assert response.json() == {"validation_error": {'orders': [{"id": 2}, ]}}
        assert response.status_code == 400

    def test_incorrect_weight(self):
        json = self.JSON
        json['data'][0]['order_id'] = 2
        json['data'][0]['weight'] = 143
        response = requests.post(self.URL, json=json)
        assert response.json() == {"validation_error": {'orders': [{"id": 2}, ]}}
        assert response.status_code == 400

    def test_incorrect_weight_float(self):
        json = self.JSON
        json['data'][0]['order_id'] = 2
        json['data'][0]['weight'] = 143.123
        response = requests.post(self.URL, json=json)
        assert response.json() == {"validation_error": {'orders': [{"id": 2}, ]}}
        assert response.status_code == 400

    def test_incorrect_region_type(self):
        json = self.JSON
        json['data'][0]['order_id'] = 2
        json['data'][0]['region'] = '1'
        response = requests.post(self.URL, json=json)
        assert response.json() == {"validation_error": {'orders': [{"id": 2}, ]}}
        assert response.status_code == 400

    def test_incorrect_delivery_hours_type(self):
        json = self.JSON
        json['data'][0]['order_id'] = 2
        json['data'][0]['delivery_hours'] = 'abrakadabra'
        response = requests.post(self.URL, json=json)
        assert response.json() == {"validation_error": {'orders': [{"id": 2}, ]}}
        assert response.status_code == 400

    def test_incorrect_type_in_delivery_hours(self):
        json = self.JSON
        json['data'][0]['order_id'] = 2
        json['data'][0]['delivery_hours'] = [123, 123]
        response = requests.post(self.URL, json=json)
        assert response.json() == {"validation_error": {'orders': [{"id": 2}, ]}}
        assert response.status_code == 400

    def test_incorrect_delivery_hours_format_zeros(self):
        json = self.JSON
        json['data'][0]['order_id'] = 2
        json['data'][0]['delivery_hours'] = ['2:00-23:00']
        response = requests.post(self.URL, json=json)
        assert response.json() == {"validation_error": {'orders': [{"id": 2}, ]}}
        assert response.status_code == 400

    def test_incorrect_delivery_hours_format_interval(self):
        json = self.JSON
        json['data'][0]['order_id'] = 2
        json['data'][0]['delivery_hours'] = ['22:00-13:00']
        response = requests.post(self.URL, json=json)
        assert response.json() == {"validation_error": {'orders': [{"id": 2}, ]}}
        assert response.status_code == 400

    def test_incorrect_delivery_hours_format_split(self):
        json = self.JSON
        json['data'][0]['order_id'] = 2
        json['data'][0]['delivery_hours'] = ['02:0013:00']
        response = requests.post(self.URL, json=json)
        assert response.json() == {"validation_error": {'orders': [{"id": 2}, ]}}
        assert response.status_code == 400
