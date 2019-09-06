from django.test import SimpleTestCase, Client

class UrlsTestCase(SimpleTestCase):
    
    def test_home_url_is_rsolved(self):
        client = Client()
        response = client.post('',{})
        self.assertEquals(response.status_code, 200)
        response = client.post('/home/',{})
        self.assertEquals(response.status_code, 200)
