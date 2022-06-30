from locust import HttpUser, task, between, User


class User1(HttpUser):
    host = "https://http.cat"
    wait_time = between(5,10)
    
    @task
    def visit_homepage(self):
        self.client.get(url="/100")
    
    @task
    def visit_indexpage(self):
        self.client.get(url="/300")
    

class User2(HttpUser):
    host = "https://http.cat"
    wait_time = between(5,10)
    
    @task
    def visit_indexpage(self):
        self.client.get(url="/400")
    

class User3(User):
    host = "https://http.cat"
    wait_time = between(5,10)
    
