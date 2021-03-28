import requests


class TestAddCouriers:
    URL = 'http://127.0.0.1:8080/couriers'
    JSON = {'data': [{'courier_id': 1,
                      'courier_type': 'car',
                      'regions': [1, 2, 3],
                      'working_hours': ['09:00-21:00', ]}]}

    def test_correct_courier(self):
        response = requests.post(self.URL, json=self.JSON)
        assert response.json() == {"couriers": [{"id": 1}, ]}
        assert response.status_code == 201

    def test_courier_id(self):
        response = requests.post(self.URL, json=self.JSON)
        assert response.json() == {"validation_error": {'couriers': [{"id": 1}, ]}}
        assert response.status_code == 400

    def test_incorrect_courier_type(self):
        json = self.JSON
        json['data'][0]['courier_id'] = 2
        json['data'][0]['courier_type'] = 'abrakadabra'
        response = requests.post(self.URL, json=json)
        assert response.json() == {"validation_error": {'couriers': [{"id": 2}, ]}}
        assert response.status_code == 400

    def test_incorrect_courier_type_type(self):
        json = self.JSON
        json['data'][0]['courier_id'] = 2
        json['data'][0]['courier_type'] = 132
        response = requests.post(self.URL, json=json)
        assert response.json() == {"validation_error": {'couriers': [{"id": 2}, ]}}
        assert response.status_code == 400

    def test_incorrect_regions_type(self):
        json = self.JSON
        json['data'][0]['courier_id'] = 2
        json['data'][0]['regions'] = '132'
        response = requests.post(self.URL, json=json)
        assert response.json() == {"validation_error": {'couriers': [{"id": 2}, ]}}
        assert response.status_code == 400

    def test_incorrect_type_in_regions(self):
        json = self.JSON
        json['data'][0]['courier_id'] = 2
        json['data'][0]['regions'] = ['abrakadabra']
        response = requests.post(self.URL, json=json)
        assert response.json() == {"validation_error": {'couriers': [{"id": 2}, ]}}
        assert response.status_code == 400

    def test_incorrect_working_hours_type(self):
        json = self.JSON
        json['data'][0]['courier_id'] = 2
        json['data'][0]['working_hours'] = 'abrakadabra'
        response = requests.post(self.URL, json=json)
        assert response.json() == {"validation_error": {'couriers': [{"id": 2}, ]}}
        assert response.status_code == 400

    def test_incorrect_type_in_working_hours(self):
        json = self.JSON
        json['data'][0]['courier_id'] = 2
        json['data'][0]['working_hours'] = [123, 123]
        response = requests.post(self.URL, json=json)
        assert response.json() == {"validation_error": {'couriers': [{"id": 2}, ]}}
        assert response.status_code == 400

    def test_incorrect_working_hours_format_zeros(self):
        json = self.JSON
        json['data'][0]['courier_id'] = 2
        json['data'][0]['working_hours'] = ['2:00-23:00']
        response = requests.post(self.URL, json=json)
        assert response.json() == {"validation_error": {'couriers': [{"id": 2}, ]}}
        assert response.status_code == 400

    def test_incorrect_working_hours_format_interval(self):
        json = self.JSON
        json['data'][0]['courier_id'] = 2
        json['data'][0]['working_hours'] = ['22:00-13:00']
        response = requests.post(self.URL, json=json)
        assert response.json() == {"validation_error": {'couriers': [{"id": 2}, ]}}
        assert response.status_code == 400

    def test_incorrect_working_hours_format_split(self):
        json = self.JSON
        json['data'][0]['courier_id'] = 2
        json['data'][0]['working_hours'] = ['02:0013:00']
        response = requests.post(self.URL, json=json)
        assert response.json() == {"validation_error": {'couriers': [{"id": 2}, ]}}
        assert response.status_code == 400
