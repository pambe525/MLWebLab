from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from django.test import tag
from selenium.webdriver.support.ui import Select


@tag('selenium')
class HomeViewTemplateTestCase(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser = webdriver.Chrome()
        cls.browser.implicitly_wait(10)
        cls.browser.get('http://localhost:8000')

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()
        
    def test_flowchart_container_is_not_visible(self):
        self.assertTrue('Machine Learning Lab' in self.browser.title)
        flow_container = self.browser.find_element_by_id('flow_container')
        self.assertEquals(flow_container.get_attribute('class'), 'invisible')

    def test_file_selector_has_placeholder(self):
        file_selector = self.browser.find_element_by_name('input_file')
        default = Select(file_selector).all_selected_options[0].text
        self.assertEquals(default, 'Select data file ...')

    def test_file_selector_contains_datafile_names(self):
        file_selector = self.browser.find_element_by_name('input_file')
        filelist = Select(file_selector).options
        self.assertGreater(len(filelist), 5)
        self.assertTrue("ex1data1.txt" in [opt.text for opt in filelist])

    def test_file_select_button_clicked_with_no_selection(self):
        file_select_btn = self.browser.find_element_by_css_selector('button.btn.btn-primary')
        file_select_btn.click()
        flow_container = self.browser.find_element_by_id('flow_container')
        self.assertEquals(flow_container.get_attribute('class'), 'invisible')

 
        