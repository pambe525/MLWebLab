import csv
import os

from django.test import tag, SimpleTestCase
from selenium import webdriver
from selenium.webdriver.support.ui import Select

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
        self.verify_selected_file()

    def test_select_button_clicked_with_no_file_selected(self):
        file_select_btn = self.browser.find_element_by_id('select_btn')
        file_select_btn.click()
        self.verify_content_area_is_visible(False)
        self.verify_selected_file()

    def test_select_button_clicked_with_file_selected(self):
        self.select_a_file(self.get_fake_data(), self.fake_datafile)
        self.verify_content_area_is_visible(True)
        self.verify_selected_file(self.fake_datafile)
        self.verify_active_tab("nav-summary-tab")

    def test_selection_change_hides_content_area(self):
        self.select_a_file(self.get_fake_data(), self.fake_datafile)
        # Re-select a file
        file_selector = self.browser.find_element_by_name('data_file')
        Select(file_selector).select_by_visible_text(constants.FILE_SELECT_DEFAULT)
        self.verify_content_area_is_visible(False)

    def test_message_dialog_when_bad_data_in_file(self):
        self.select_a_file([], self.fake_datafile)
        self.verify_message_box_and_close("No columns to parse from file")
        self.verify_content_area_is_visible(False)
        self.verify_selected_file(self.fake_datafile)

    def test_message_dialog_when_data_file_has_no_headers(self):
        csv_data = self.get_fake_data()
        del csv_data[0]  # remove headers
        self.select_a_file(csv_data, self.fake_datafile)
        self.verify_message_box_and_close("Data file has no headers")
        self.verify_content_area_is_visible(False)
        self.verify_selected_file(self.fake_datafile)

    def test_data_summary_on_selected_file(self):
        csv_data = self.get_fake_data()
        self.select_a_file(csv_data, self.fake_datafile)
        self.verify_source_file_data(self.fake_datafile, 10, 4)
        self.verify_column_name_selector(csv_data[0])
        self.verify_selected_column_stats(['int64', 1, 37, 19, 12.11])
        self.verify_selected_column_values(list(range(1, 18, 4)))
        self.verify_histogram_plot()
        self.select_column_name("col3")
        self.verify_selected_column_stats(['int64', 3, 39, 21, 12.11])
        self.verify_selected_column_values(list(range(3, 20, 4)))
        self.verify_histogram_plot()

    def test_train_button_clicked_with_default_settings(self):
        csv_data = [["X1", "X2", "Y"], [0, 9, 24], [1, 8, 23], [2, 7, 22], [3, 6, 21], [4, 5, 20], [5, 4, 19],
                    [6, 3, 18], [7, 2, 17], [8, 1, 16], [9, 0, 15]]
        self.select_a_file(csv_data, self.fake_datafile)
        self.browser.find_element_by_id("nav-train-tab").click()
        self.browser.find_element_by_id("train_btn").click()
        self.browser.implicitly_wait(2)
        self.assertFalse(self.browser.find_element_by_id("glass_pane").is_displayed())
        self.verify_content_area_is_visible(True)
        self.verify_selected_file(self.fake_datafile)
        self.verify_active_tab("nav-train-tab")
        self.verify_training_set_data('Y', '5')
        self.verify_method_data("Linear Regression")
        self.verify_validation_metrics()
        self.verify_validation_plots()
        self.verify_source_file_data(self.fake_datafile, 10, 3)

    def test_train_button_clicked_with_exception(self):
        csv_data = [["X1", "X2", "Y"], [0, None, 15], [1, 4, 16], [2, 3, 17], [3, None, 18], [4, 1, 19],
                    [5, 0, 20],[6, 10, 15], [1, 4, 16], [2, 3, 17], [3, 9, 18]]
        self.select_a_file(csv_data, self.fake_datafile)
        self.browser.find_element_by_id("nav-train-tab").click()
        self.browser.find_element_by_id("train_btn").click()
        self.browser.implicitly_wait(2)
        self.assertFalse(self.browser.find_element_by_id("glass_pane").is_displayed())
        self.verify_message_box_and_close("Input contains NaN")
        self.verify_content_area_is_visible(True)
        self.verify_selected_file(self.fake_datafile)
        self.verify_active_tab("nav-train-tab")
        self.verify_training_set_data('Y', '5')
        self.verify_method_data("Linear Regression")

    # ------------------------------------------------------------------------------------------------------------------
    # HELPER METHODS
    # ------------------------------------------------------------------------------------------------------------------

    def get_fake_data(self):
        data_list = [["col1", "col2", "col3", "col4"]]
        for i in range(1, 40, 4):
            data_list.append(list(range(i,i+4)))
        return data_list

    def write_csvfile(self, csv_data):
        with open(self.datafile_path, mode='w+') as csv_file:
            writer = csv.writer(csv_file, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
            writer.writerows(csv_data)
        csv_file.close()

    def select_a_file(self, csv_data, file_name):
        self.write_csvfile(csv_data)
        file_selector = self.browser.find_element_by_name('data_file')
        Select(file_selector).select_by_visible_text(file_name)
        file_select_btn = self.browser.find_element_by_id('select_btn')
        file_select_btn.click()

    def verify_content_area_is_visible(self, is_visible):
        container = self.browser.find_element_by_id('home_container')
        if is_visible:
            self.assertFalse('invisible' in container.get_attribute('class'))
        else:
            self.assertTrue('invisible' in container.get_attribute('class'))

    def verify_selected_file(self, default_selection=constants.FILE_SELECT_DEFAULT):
        file_selector = self.browser.find_element_by_name('data_file')
        selection = Select(file_selector).first_selected_option.text
        self.assertEquals(default_selection, selection)

    def verify_source_file_data(self, file_name, rows, cols):
        self.browser.find_element_by_id("nav-summary-tab").click()
        self.assertEquals(file_name, self.browser.find_element_by_id("source_file").text)
        self.assertEquals(rows, int(self.browser.find_element_by_id("source_rows").text))
        self.assertEquals(cols, int(self.browser.find_element_by_id("source_cols").text))

    def verify_column_name_selector(self, col_names):
        column_selector = self.browser.find_element_by_id("column_name_select")
        options = [x.text for x in column_selector.find_elements_by_tag_name("option")]
        self.assertEqual(options, col_names)
        selected_option = Select(column_selector).first_selected_option.text
        self.assertEqual(selected_option, col_names[0])

    def select_column_name(self, col_name):
        column_selector = self.browser.find_element_by_id("column_name_select")
        Select(column_selector).select_by_visible_text(col_name)

    def verify_selected_column_stats(self, col_stats):
        col_stats = [str(x) for x in col_stats]
        stats_table = self.browser.find_element_by_id("column_stats_table")
        rows = stats_table.find_elements_by_tag_name("tr")
        metrics = [row.find_elements_by_tag_name("td")[1].text for row in rows]
        self.assertEqual(metrics, col_stats)

    def verify_selected_column_values(self, col_values):
        col_values = [str(x) for x in col_values]
        values_table = self.browser.find_element_by_id("column_values_table")
        rows = values_table.find_elements_by_tag_name("tr")
        values = [row.find_elements_by_tag_name("td")[1].text for row in rows]
        self.assertEqual(values, col_values)

    def verify_training_set_data(self, target_feature, n_splits):
        self.assertEquals(target_feature, self.browser.find_element_by_id("target_feature").text)
        splits_selector = self.browser.find_element_by_name('n_splits')
        selection = Select(splits_selector).first_selected_option.text
        self.assertEquals(n_splits, selection)

    def verify_method_data(self, training_method):
        self.assertEquals(training_method, self.browser.find_element_by_name("training_method").text)

    def verify_validation_set_data(self, validation_rows):
        self.assertEquals(validation_rows, int(self.browser.find_element_by_id("validation_rows").text))

    def verify_active_tab(self, tab_id):
        self.assertTrue("active" in self.browser.find_element_by_id(tab_id).get_attribute("class"))

    def verify_validation_metrics(self):
        self.browser.find_element_by_id("nav-train-tab").click()
        self.assertEqual(self.browser.find_element_by_name("training_method").text, "Linear Regression")
        self.assertGreater(float(self.browser.find_element_by_id("test_score").text), 0)
        self.assertGreater(float(self.browser.find_element_by_id("train_score").text), 0)
        self.assertGreaterEqual(float(self.browser.find_element_by_id("train_scores_stdev").text), 0.0)
        self.assertGreaterEqual(float(self.browser.find_element_by_id("test_scores_stdev").text), 0.0)

    def verify_validation_plots(self):
        plot = self.browser.find_element_by_id("validation_plot").find_element_by_class_name("plotly")
        self.assertIsNotNone(plot)

    def verify_message_box_and_close(self, message_text):
        message_box = self.browser.find_element_by_id("msg_box")
        self.assertTrue(message_box.is_displayed())
        close_button = self.browser.find_element_by_id("msg_box_close")
        self.assertTrue(message_text in self.browser.find_element_by_id("msg_text").text)
        close_button.click()
        self.assertFalse(message_box.is_displayed())

    def verify_histogram_plot(self):
        plot = self.browser.find_element_by_id("column_histogram").find_element_by_class_name("plotly")
        self.assertIsNotNone(plot)