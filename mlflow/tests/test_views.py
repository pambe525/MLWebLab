from django.test import SimpleTestCase
from django.urls import reverse
from mlflow.forms import DataFileForm

class HomeViewTestCase(SimpleTestCase):

    def test_initial_home_view_get(self):
        response = self.client.get(reverse("home"))
        form = response.context['form']
        self.assertEquals(response.context['select_btn_disabled'], '')
        self.assertEquals(response.context['change_btn_disabled'], 'disabled')
        self.assertEquals(response.context['flow_chart_visibility'], 'invisible')
        self.assertFalse(form.fields['data_file'].disabled)
        self.assertEquals(form.fields['data_file'].initial, "Choose a file...")
        self.assertGreater(len(form.fields['data_file'].choices), 5)

    def test_home_view_post_with_default_selection(self):
        response = self.client.post(reverse("home"), {'data_file': 'Choose a file...', 'data': ['select_btn']})
        form = response.context['form']
        self.assertTrue(form.is_valid())
        self.assertTrue(form.is_bound)
        self.assertEquals(response.context['select_btn_disabled'], '')
        self.assertEquals(response.context['change_btn_disabled'], 'disabled')
        self.assertEquals(response.context['flow_chart_visibility'], 'invisible')
        self.assertFalse(form.fields['data_file'].disabled)

    def test_home_view_post_with_file_selected(self):
        response = self.client.post(reverse("home"), {'data_file': 'ex1data1.txt'})
        form = response.context['form']
        self.assertTrue(form.is_valid())
        self.assertTrue(form.is_bound)
        self.assertEquals(response.context['select_btn_disabled'], 'disabled')
        self.assertEquals(response.context['change_btn_disabled'], '')
        self.assertEquals(response.context['flow_chart_visibility'], 'visible')
        self.assertTrue(form.fields['data_file'].disabled)
        self.assertEquals(form.fields['data_file'].initial, "ex1data1.txt")

