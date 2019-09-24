from django.test import SimpleTestCase
from django.urls import reverse


class HomeViewTestCase(SimpleTestCase):

    def test_initial_home_view_get(self):
        response = self.client.get(reverse("home"))
        form = response.context['form']
        self.assertGreater(len(form.fields['data_file'].choices), 5)
        self.verify_widget_states_with_selection_enabled(response, True)

    def test_home_view_post_with_default_selection(self):
        response = self.client.post(reverse("home"), {'data_file': 'Choose a file...', 'data': ['select_btn']})
        form = response.context['form']
        self.assertTrue(form.is_valid())
        self.assertTrue(form.is_bound)
        self.verify_widget_states_with_selection_enabled(response, True)

    def test_home_view_post_with_file_selected(self):
        response = self.client.post(reverse("home"), {'data_file': 'ex1data1.txt'})
        form = response.context['form']
        self.assertTrue(form.is_valid())
        self.assertTrue(form.is_bound)
        self.verify_widget_states_with_selection_enabled(response, False, 'ex1data1.txt')
        self.verify_source_file_data(response, 'ex1data1.txt', 97, 2)

    # ------------------------------------------------------------------------------------------------------------------
    # HELPER METHODS
    # ------------------------------------------------------------------------------------------------------------------

    def verify_widget_states_with_selection_enabled(self, response, is_enabled, placeholder="Choose a file..."):
        form = response.context['form']
        if is_enabled:
            self.assertEquals(response.context['select_btn_disabled'], '')
            self.assertEquals(response.context['change_btn_disabled'], 'disabled')
            self.assertEquals(response.context['flow_chart_visibility'], 'invisible')
            self.assertFalse(form.fields['data_file'].disabled)
        else:
            self.assertEquals(response.context['select_btn_disabled'], 'disabled')
            self.assertEquals(response.context['change_btn_disabled'], '')
            self.assertEquals(response.context['flow_chart_visibility'], 'visible')
            self.assertTrue(form.fields['data_file'].disabled)
        self.assertEquals(form.fields['data_file'].initial, placeholder)

    def verify_source_file_data(self, response, file_name, rows, cols):
        self.assertEquals(file_name, response.context['data_file_name'])
        self.assertEquals(rows, response.context['data_file_rows'])
        self.assertEquals(cols, response.context['data_file_cols'])
