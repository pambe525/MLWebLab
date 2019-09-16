from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from django.test import tag
from selenium.webdriver.support.ui import Select


@tag('selenium')
class HomeViewTemplateTestCase(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser = webdriver.Firefox()

    def setUp(self):
        self.browser.implicitly_wait(10)
        self.browser.get('http://localhost:8000/')

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def test_initial_state_of_view(self):
        self.assertTrue('Machine Learning Lab' in self.browser.title)
        self.verify_flowchart_is_visible(False)
        # File Selector contains data file names
        file_list = Select(self.browser.find_element_by_name('data_file')).options
        self.assertGreater(len(file_list), 5)
        self.assertTrue("ex1data1.txt" in [opt.text for opt in file_list])
        self.verify_file_selection_enabled(True)

    def test_file_select_button_clicked_with_no_selection(self):
        file_select_btn = self.browser.find_element_by_name('select_btn')
        file_select_btn.click()
        self.verify_flowchart_is_visible(False)
        self.verify_file_selection_enabled(True)

    def test_file_select_button_clicked_with_file_selection(self):
        self.select_a_file('ex1data1.txt')
        self.verify_flowchart_is_visible(True)
        self.verify_file_selection_enabled(False, 'ex1data1.txt')

    def test_change_file_button_clicked(self):
        self.select_a_file('ex1data1.txt')
        self.browser.find_element_by_name('change_btn').click()
        self.verify_flowchart_is_visible(False)
        self.verify_file_selection_enabled(True)

    # ------------------------------------------------------------------------------------------------------------------
    # HELPER METHODS
    # ------------------------------------------------------------------------------------------------------------------

    def verify_flowchart_is_visible(self, is_visible):
        flow_container = self.browser.find_element_by_id('flow_container')
        if is_visible:
            self.assertFalse('invisible' in flow_container.get_attribute('class'))
        else:
            self.assertTrue('invisible' in flow_container.get_attribute('class'))

    def verify_file_selection_enabled(self, is_enabled, default_selection="Choose a file..."):
        select_btn = self.browser.find_element_by_name('select_btn')
        change_btn = self.browser.find_element_by_name('change_btn')
        file_selector = self.browser.find_element_by_name('data_file')
        selection = Select(file_selector).first_selected_option.text
        self.assertEquals(default_selection, selection)
        if is_enabled:
            self.assertTrue(select_btn.is_enabled() and not change_btn.is_enabled() and file_selector.is_enabled())
        else:
            self.assertTrue(not select_btn.is_enabled() and change_btn.is_enabled() and not file_selector.is_enabled())

    def select_a_file(self, file_name):
        file_selector = self.browser.find_element_by_name('data_file')
        Select(file_selector).select_by_visible_text(file_name)
        file_select_btn = self.browser.find_element_by_name('select_btn')
        file_select_btn.click()
