from locust import HttpUser, task, between


class LoadTestUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task
    def post_get_item(self):
        item = {'id': 0,'name':'name', 'price': 10, 'deleted': False}
        headers = {'Content-Type': 'application/json'}
        response = self.client.post("/item", json=item, headers=headers)
        new_id = response.json()['id']
        self.client.get(f'/item/{new_id}')

    def post_cart(self):
        cart = {}
        headers = {'Content-Type': 'application/json'}
        self.client.post("/cart", json=cart, headers=headers)
