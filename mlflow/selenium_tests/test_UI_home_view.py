from selenium import webdriver
from django.test import tag, SimpleTestCase
from selenium.webdriver.support.ui import Select
import csv
import os
from django.conf import settings
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from mlflow import constants


@tag('selenium')
class HomeViewTemplateTestCase(SimpleTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser = webdriver.Firefox()
        # Create a empty fake data file so it appears in selection list
        cls.fake_datafile = "fake_data"
        cls.datafile_path = os.path.join(constants.DATA_FILE_PATH, cls.fake_datafile)
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
        self.verify_content_area_is_visible(False)
        # File Selector contains data file names
        file_list = Select(self.browser.find_element_by_name('data_file')).options
        self.assertGreater(len(file_list), 5)
        self.assertTrue(self.fake_datafile in [opt.text for opt in file_list])
        self.verify_file_selection_enabled(True)

    def test_select_button_clicked_with_no_file_selected(self):
        file_select_btn = self.browser.find_element_by_name('select_btn')
        file_select_btn.click()
        self.verify_content_area_is_visible(False)
        self.verify_file_selection_enabled(True)

    def test_select_button_clicked_with_file_selected(self):
        csv_data = [["col1", "col2", "col3", "col4"], [1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]
        self.write_csvfile(csv_data)
        self.select_a_file(self.fake_datafile)
        self.verify_content_area_is_visible(True)
        self.verify_file_selection_enabled(False, self.fake_datafile)
        self.verify_source_file_data(self.fake_datafile, 3, 4)
        self.verify_training_set_data('col4', 3, '80%', 2)
        self.verify_method_data("Linear Regression")
        self.verify_validation_set_data(1)
        self.verify_tabs()

    def test_change_file_button_clicked(self):
        csv_data = [["col1", "col2", "col3", "col4"], [1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]
        self.write_csvfile(csv_data)
        self.select_a_file(self.fake_datafile)
        self.browser.find_element_by_name('change_btn').click()
        self.verify_content_area_is_visible(False)
        self.verify_file_selection_enabled(True)

    def test_message_dialog_when_bad_data_in_file(self):
        self.write_csvfile([])
        self.select_a_file(self.fake_datafile)
        self.verify_message_box_and_close("No columns to parse from file")
        self.verify_content_area_is_visible(False)
        self.verify_file_selection_enabled(True, self.fake_datafile)

    def test_message_dialog_when_data_file_has_no_headers(self):
        csv_data = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]
        self.write_csvfile(csv_data)
        self.select_a_file(self.fake_datafile)
        self.verify_message_box_and_close("Data file has no headers")
        self.verify_content_area_is_visible(False)
        self.verify_file_selection_enabled(True, self.fake_datafile)

    def test_train_button_clicked_with_default_settings(self):
        csv_data = [["X1", "X2", "Y"], [0, 9, 24], [1, 8, 23], [2, 7, 22], [3, 6, 21], [4, 5, 20], [5, 4, 19],
                    [6, 3, 18], [7, 2, 17], [8, 1, 16], [9, 0, 15]]
        self.write_csvfile(csv_data)
        self.select_a_file(self.fake_datafile)
        self.browser.find_element_by_name("train_btn").click()
        self.assertFalse(self.browser.find_element_by_id("glass_pane").is_displayed())
        self.verify_content_area_is_visible(True)
        self.verify_file_selection_enabled(False, self.fake_datafile)
        self.verify_training_set_data('Y', 2, '80%', 8)
        self.verify_method_data("Linear Regression")
        self.verify_tabs(True)
        self.verify_validation_tab()
        self.verify_source_file_data(self.fake_datafile, 10, 3)

    def test_train_button_clicked_with_exception(self):
        csv_data = [["X1", "X2", "Y"], [0, None, 15], [1, 4, 16], [2, 3, 17], [3, None, 18], [4, 1, 19], [5, 0, 20]]
        self.write_csvfile(csv_data)
        self.select_a_file(self.fake_datafile)
        self.browser.find_element_by_name("train_btn").click()
        self.assertFalse(self.browser.find_element_by_id("glass_pane").is_displayed())
        self.verify_message_box_and_close("Input contains NaN")
        self.verify_content_area_is_visible(True)
        self.verify_file_selection_enabled(False, self.fake_datafile)
        self.verify_training_set_data('Y', 2, '80%', 4)
        self.verify_method_data("Linear Regression")
        self.verify_tabs(False)
        self.verify_source_file_data(self.fake_datafile, 6, 3)

    # ------------------------------------------------------------------------------------------------------------------
    # HELPER METHODS
    # ------------------------------------------------------------------------------------------------------------------

    def write_csvfile(self, csv_data):
        with open(self.datafile_path, mode='w+') as csv_file:
            writer = csv.writer(csv_file, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
            writer.writerows(csv_data)
        csv_file.close()

    def verify_content_area_is_visible(self, is_visible):
        container = self.browser.find_element_by_id('home_container')
        if is_visible:
            self.assertFalse('invisible' in container.get_attribute('class'))
        else:
            self.assertTrue('invisible' in container.get_attribute('class'))

    def verify_file_selection_enabled(self, is_enabled, default_selection=constants.FILE_SELECT_DEFAULT):
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
        self.browser.find_element_by_id("nav-explore-tab").click()
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

    def verify_validation_set_data(self, validation_rows):
        self.assertEquals(validation_rows, int(self.browser.find_element_by_name("validation_rows").text))

    def verify_tabs(self, has_validation=False):
        if not has_validation:
            self.assertTrue("active" in self.browser.find_element_by_id("nav-explore-tab").get_attribute("class"))
            self.assertTrue("disabled" in self.browser.find_element_by_id("nav-validate-tab").get_attribute("class"))
        else:
            self.assertFalse("disabled" in self.browser.find_element_by_id("nav-validate-tab").get_attribute("class"))
            self.assertTrue("active" in self.browser.find_element_by_id("nav-validate-tab").get_attribute("class"))

    def verify_validation_tab(self):
        self.assertEqual(self.browser.find_element_by_name("training_method").text, "Linear Regression")
        self.assertGreater(float(self.browser.find_element_by_name("validation_score").text), 0)
        self.assertGreater(float(self.browser.find_element_by_name("training_score").text), 0)

    def verify_message_box_and_close(self, message_text):
        message_box = self.browser.find_element_by_id("msg_box")
        self.assertTrue(message_box.is_displayed())
        close_button = self.browser.find_element_by_id("msg_box_close")
        self.assertTrue(message_text in self.browser.find_element_by_id("msg_text").text)
        close_button.click()
        self.assertFalse(message_box.is_displayed())
