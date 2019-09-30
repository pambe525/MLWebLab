from selenium import webdriver
from django.test import tag, SimpleTestCase
from selenium.webdriver.support.ui import Select
import csv
import os
from django.conf import settings
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

@tag('selenium')
class HomeViewTemplateTestCase(SimpleTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser = webdriver.Firefox()
        # Create a empty fake data file so it appears in selection list
        cls.fake_datafile = "fake_data.csv"
        cls.datafile_path = os.path.join(settings.BASE_DIR, "data/" + cls.fake_datafile)
        open(cls.datafile_path, 'a+').close()

    def setUp(self):
        self.browser.implicitly_wait(10)
        self.browser.get('http://localhost:8000/')

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()
        os.remove(cls.datafile_path)

    def test_initial_view(self):
        self.assertTrue('Machine Learning Lab' in self.browser.title)
        self.verify_flowchart_is_visible(False)
        # File Selector contains data file names
        file_list = Select(self.browser.find_element_by_name('data_file')).options
        self.assertGreater(len(file_list), 5)
        self.assertTrue(self.fake_datafile in [opt.text for opt in file_list])
        self.verify_file_selection_enabled(True)

    def test_select_button_clicked_with_no_file_selected(self):
        file_select_btn = self.browser.find_element_by_name('select_btn')
        file_select_btn.click()
        self.verify_flowchart_is_visible(False)
        self.verify_file_selection_enabled(True)

    def test_select_button_clicked_with_file_selected(self):
        csv_data = [["col1", "col2", "col3", "col4"], [1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]
        self.write_csvfile(csv_data)
        self.select_a_file(self.fake_datafile)
        self.verify_flowchart_is_visible(True)
        self.verify_file_selection_enabled(False, self.fake_datafile)
        self.verify_source_file_data(self.fake_datafile, 3, 4)
        self.verify_training_set_data('col4', 3, '80%', 2)
        self.verify_method_data("Linear Regression")
        self.verify_validation_set_data(1)

    def test_change_file_button_clicked(self):
        csv_data = [["col1", "col2", "col3", "col4"], [1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]
        self.write_csvfile(csv_data)
        self.select_a_file(self.fake_datafile)
        self.browser.find_element_by_name('change_btn').click()
        self.verify_flowchart_is_visible(False)
        self.verify_file_selection_enabled(True)

    def test_message_dialog_when_bad_data_in_file(self):
        self.write_csvfile([])
        self.select_a_file(self.fake_datafile)
        self.verify_message_box_and_close("No columns to parse from file")
        self.verify_flowchart_is_visible(False)
        self.verify_file_selection_enabled(True, self.fake_datafile)

    def test_message_dialog_when_data_file_has_no_headers(self):
        csv_data = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]
        self.write_csvfile(csv_data)
        self.select_a_file(self.fake_datafile)
        self.verify_message_box_and_close("Data file has no headers")
        self.verify_flowchart_is_visible(False)
        self.verify_file_selection_enabled(True, self.fake_datafile)

    # ------------------------------------------------------------------------------------------------------------------
    # HELPER METHODS
    # ------------------------------------------------------------------------------------------------------------------

    def write_csvfile(self, csv_data):
        with open(self.datafile_path, mode='w+') as csv_file:
            writer = csv.writer(csv_file, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
            writer.writerows(csv_data)
        csv_file.close()

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

    def verify_source_file_data(self, file_name, rows, cols):
        self.assertEquals(file_name, self.browser.find_element_by_name("source_file").text)
        self.assertEquals(rows, int(self.browser.find_element_by_name("source_rows").text))
        self.assertEquals(cols, int(self.browser.find_element_by_name("source_cols").text))

    def verify_training_set_data(self, target_feature, base_features, training_ratio, training_rows):
        self.assertEquals(target_feature, self.browser.find_element_by_name("target_feature").text)
        self.assertEquals(base_features, int(self.browser.find_element_by_name("base_features").text))
        self.assertEquals(training_ratio, self.browser.find_element_by_name("training_ratio").text)
        self.assertEquals(training_rows, int(self.browser.find_element_by_name("training_rows").text))

    def verify_method_data(self, training_method):
        self.assertEquals(training_method, self.browser.find_element_by_name("training_method").text)

    def verify_validation_set_data(self, validation_rows, validation_score=''):
        self.assertEquals(validation_rows, int(self.browser.find_element_by_name("validation_rows").text))
        self.assertEquals(validation_score, self.browser.find_element_by_name("validation_score").text)
        self.assertTrue(self.browser.find_element_by_id("warning_icon").is_displayed())
        self.assertFalse(self.browser.find_element_by_id("check_icon").is_displayed())
        self.assertFalse(self.browser.find_element_by_name("predict_btn").is_enabled())

    def verify_message_box_and_close(self, message_text):
        message = self.browser.switch_to.active_element
        self.assertTrue(message.is_displayed())
        btnXPath = "//button[contains(text(),'Close')]"
        close_button = WebDriverWait(self.browser, 10).until(EC.element_to_be_clickable((By.XPATH, btnXPath)))
        self.assertEqual(self.browser.find_element_by_class_name("modal-body").text, message_text)
        close_button.click()