import csv
import os

from django.test import tag, SimpleTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait

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
        self.browser.get('http://localhost:8000/')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        os.remove(cls.datafile_path)
        cls.browser.quit()

    # INITIAL UI STATE
    def test_initial_view(self):
        self.assertTrue('Machine Learning Lab' in self.browser.title)
        self.verify_glass_pane_is_visible(False)
        self.verify_msgbox_is_visible(False)
        self.verify_content_area_is_visible(False)
        # File Selector contains data file names
        file_list = Select(self.browser.find_element_by_name('data_file')).options
        self.assertGreater(len(file_list), 5)
        self.assertTrue(self.fake_datafile in [opt.text for opt in file_list])
        self.verify_selected_file()

    # ========================================================================================
    # DATA FILE SELECTION TESTS
    # ----------------------------------------------------------------------------------------
    def test_select_button_click_ignored_with_no_file_selected(self):
        file_select_btn = self.browser.find_element_by_id('select_btn')
        file_select_btn.click()
        self.verify_glass_pane_is_visible(False)
        self.verify_msgbox_is_visible(False)
        self.verify_content_area_is_visible(False)
        self.verify_selected_file()

    def test_select_button_click_with_file_selected_loads_data(self):
        self.write_data_and_select_file(self.get_fake_data(), self.fake_datafile)
        #self.verify_glass_pane_is_visible(True)
        self.wait_until_visible(By.ID, "home_container")
        self.verify_content_area_is_visible(True)
        self.verify_msgbox_is_visible(False)
        self.verify_active_tab("nav-summary-tab")
        self.verify_glass_pane_is_visible(False)

    def test_selection_change_hides_content_area(self):
        self.write_data_and_select_file(self.get_fake_data(), self.fake_datafile)
        self.wait_until_visible(By.ID, "home_container")
        self.verify_content_area_is_visible(True)
        # Change file selection
        file_selector = self.browser.find_element_by_name('data_file')
        Select(file_selector).select_by_visible_text(constants.FILE_SELECT_DEFAULT)
        self.verify_content_area_is_visible(False)

    def test_message_dialog_shows_when_bad_data_in_file(self):
        self.write_data_and_select_file([], self.fake_datafile)
        self.verify_message_box_and_close("No columns to parse from file")
        self.verify_glass_pane_is_visible(False)
        self.verify_content_area_is_visible(False)

    def test_message_dialog_shows_when_data_file_has_no_headers(self):
        csv_data = self.get_fake_data()
        del csv_data[0]  # remove headers
        self.write_data_and_select_file(csv_data, self.fake_datafile)
        self.verify_message_box_and_close("Data file has no headers")
        self.verify_content_area_is_visible(False)

    def test_reselecting_last_loaded_file_redisplays_content(self):
        self.write_data_and_select_file(self.get_fake_data(), self.fake_datafile)
        self.wait_until_visible(By.ID, "home_container")
        file_selector = self.browser.find_element_by_name('data_file')
        Select(file_selector).select_by_visible_text(constants.FILE_SELECT_DEFAULT)
        Select(file_selector).select_by_visible_text(self.fake_datafile)
        self.verify_content_area_is_visible(True)

    def test_previous_msgbox_hidden_when_new_file_selected(self):
        self.write_data_and_select_file([], self.fake_datafile)  # shows message dialog
        self.write_data_and_select_file(self.get_fake_data(), self.fake_datafile)
        self.wait_until_visible(By.ID, "home_container")
        self.verify_msgbox_is_visible(False)

    # ========================================================================================
    # DATA SUMMARY TAB TESTS
    # ----------------------------------------------------------------------------------------
    def test_data_summary_tab_is_activated_when_new_file_selected(self):
        file_selector = self.browser.find_element_by_name('data_file')
        Select(file_selector).select_by_index(1)
        self.browser.find_element_by_id('select_btn').click()
        self.wait_until_visible(By.ID, "home_container")
        self.browser.find_element_by_id("nav-train-tab").click()  # change tab
        self.write_data_and_select_file(self.get_fake_data(), self.fake_datafile)
        self.wait_until_visible(By.ID, "home_container")
        self.verify_active_tab("nav-summary-tab")

    def test_data_summary_content_for_selected_file(self):
        self.write_data_and_select_file(self.get_fake_data(), self.fake_datafile)
        self.wait_until_visible(By.ID, "home_container")
        self.verify_source_file_data(self.fake_datafile, 10, 4)
        self.verify_column_stats_table(self.get_fake_data())
        self.verify_column_stats_table_row_is_highlited(0)
        self.verify_histogram_plot(0)

    def test_column_stats_table_row_selection_changes_plot(self):
        self.write_data_and_select_file(self.get_fake_data(), self.fake_datafile)
        self.wait_until_visible(By.ID, "home_container")
        self.select_file_by_index(1)
        self.wait_until_visible(By.ID, "home_container")
        columns = int(self.browser.find_element_by_id("source_cols").text)
        rows = self.browser.find_element_by_id("column_stats_table").find_elements_by_class_name("clickable-row")
        self.assertEqual(len(rows), columns)

    # def test_column_stats_table_rows_cleared_when_data_file_changes(self):
    #     self.write_data_and_select_file(self.get_fake_data(), self.fake_datafile)
    #     self.wait_until_visible(By.ID, "home_container")
    #     file_selector = self.browser.find_element_by_name('data_file')
    #
    #     self.select_column_stats_table_row(3)
    #     self.verify_column_stats_table_row_is_highlited(3)
    #     self.verify_histogram_plot(3)

    # def test_train_button_clicked_with_default_settings(self):
    #     csv_data = [["X1", "X2", "Y"], [0, 9, 24], [1, 8, 23], [2, 7, 22], [3, 6, 21], [4, 5, 20], [5, 4, 19],
    #                 [6, 3, 18], [7, 2, 17], [8, 1, 16], [9, 0, 15]]
    #     self.write_data_and_select_file(csv_data, self.fake_datafile)
    #     self.browser.find_element_by_id("nav-train-tab").click()
    #     self.browser.find_element_by_id("train_btn").click()
    #     self.browser.implicitly_wait(2)
    #     self.assertFalse(self.browser.find_element_by_id("glass_pane").is_displayed())
    #     self.verify_content_area_is_visible(True)
    #     self.verify_selected_file(self.fake_datafile)
    #     self.verify_active_tab("nav-train-tab")
    #     self.verify_training_set_data('Y', '5')
    #     self.verify_method_data("Linear Regression")
    #     self.verify_validation_metrics()
    #     self.verify_validation_plots()
    #     self.verify_source_file_data(self.fake_datafile, 10, 3)
    #
    # def test_train_button_clicked_with_exception(self):
    #     csv_data = [["X1", "X2", "Y"], [0, None, 15], [1, 4, 16], [2, 3, 17], [3, None, 18], [4, 1, 19],
    #                 [5, 0, 20], [6, 10, 15], [1, 4, 16], [2, 3, 17], [3, 9, 18]]
    #     self.write_data_and_select_file(csv_data, self.fake_datafile)
    #     self.browser.find_element_by_id("nav-train-tab").click()
    #     self.browser.find_element_by_id("train_btn").click()
    #     self.browser.implicitly_wait(2)
    #     self.assertFalse(self.browser.find_element_by_id("glass_pane").is_displayed())
    #     self.verify_message_box_and_close("Input contains NaN")
    #     self.verify_content_area_is_visible(True)
    #     self.verify_selected_file(self.fake_datafile)
    #     self.verify_active_tab("nav-train-tab")
    #     self.verify_training_set_data('Y', '5')
    #     self.verify_method_data("Linear Regression")

    # ------------------------------------------------------------------------------------------------------------------
    # HELPER METHODS
    # ------------------------------------------------------------------------------------------------------------------

    def get_fake_data(self):
        data_list = [["col1", "col2", "col3", "col4"]]
        for i in range(1, 40, 4):
            data_list.append(list(range(i, i + 4)))
        return data_list

    def write_csvfile(self, csv_data):
        with open(self.datafile_path, mode='w+') as csv_file:
            writer = csv.writer(csv_file, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
            writer.writerows(csv_data)
        csv_file.close()

    def write_data_and_select_file(self, csv_data, file_name):
        self.write_csvfile(csv_data)
        file_selector = self.browser.find_element_by_name('data_file')
        Select(file_selector).select_by_visible_text(file_name)
        file_select_btn = self.browser.find_element_by_id('select_btn')
        file_select_btn.click()

    def select_file_by_index(self, index):
        file_selector = self.browser.find_element_by_name('data_file')
        Select(file_selector).select_by_index(index)
        file_select_btn = self.browser.find_element_by_id('select_btn')
        file_select_btn.click()

    def select_column_stats_table_row(self, row_index):
        table = self.browser.find_element_by_id("column_stats_table")
        row = table.find_elements_by_class_name("clickable-row")[row_index]
        row.find_elements_by_tag_name("td")[0].click()

    def wait_until_visible(self, by, id):
        wait = WebDriverWait(self.browser, 10)
        return wait.until(EC.visibility_of_element_located((by, id)))

    def verify_glass_pane_is_visible(self, is_visible=True):
        glass_pane = self.browser.find_element_by_id('glass_pane')
        self.assertTrue(glass_pane.is_displayed()) if is_visible else self.assertFalse(glass_pane.is_displayed())

    def verify_msgbox_is_visible(self, is_visible=True):
        msg_box = self.browser.find_element_by_id('msg_box')
        self.assertTrue(msg_box.is_displayed()) if is_visible else self.assertFalse(msg_box.is_displayed())

    def verify_message_box_and_close(self, message_text):
        message_box = self.browser.find_element_by_id("msg_box")
        self.assertTrue(message_box.is_displayed())
        close_button = self.browser.find_element_by_id("msg_box_close")
        self.assertTrue(message_text in self.browser.find_element_by_id("msg_text").text)
        close_button.click()
        self.assertFalse(message_box.is_displayed())

    def verify_content_area_is_visible(self, is_visible):
        container = self.browser.find_element_by_id('home_container')
        div_class = container.get_attribute('class')
        self.assertFalse('invisible' in div_class) if is_visible else self.assertTrue('invisible' in div_class)

    def verify_active_tab(self, tab_id):
        self.assertTrue("active" in self.browser.find_element_by_id(tab_id).get_attribute("class"))

    def verify_selected_file(self, default_selection=constants.FILE_SELECT_DEFAULT):
        file_selector = self.browser.find_element_by_name('data_file')
        selection = Select(file_selector).first_selected_option.text
        self.assertEquals(default_selection, selection)

    def verify_source_file_data(self, file_name, rows, cols):
        self.browser.find_element_by_id("nav-summary-tab").click()
        self.assertEquals(file_name, self.browser.find_element_by_id("source_file").text)
        self.assertEquals(rows, int(self.browser.find_element_by_id("source_rows").text))
        self.assertEquals(cols, int(self.browser.find_element_by_id("source_cols").text))

    def verify_column_stats_table(self, data_table):
        column_stats_table = self.browser.find_element_by_id("column_stats_table")
        rows = column_stats_table.find_elements_by_class_name("clickable-row")
        for index, row in enumerate(rows):
            cells = row.find_elements_by_tag_name("td")
            self.assertEqual(cells[0].text, data_table[0][index])
            self.assertEqual(cells[1].text, 'int64')
            self.assertEqual(cells[2].text, str(index + 1))
            self.assertEqual(cells[3].text, str(index + 37))
            self.assertEqual(cells[4].text, str(index + 19))
            self.assertEqual(cells[5].text, '12.11')

    def verify_column_stats_table_row_is_highlited(self, data_row_index):
        column_stats_table = self.browser.find_element_by_id("column_stats_table")
        rows = column_stats_table.find_elements_by_class_name('clickable-row')
        self.assertEqual(rows[data_row_index].value_of_css_property('background-color'), 'rgb(173, 216, 230)')

    def verify_histogram_plot(self, data_row_index):
        column_stats_table = self.browser.find_element_by_id("column_stats_table")
        rows = column_stats_table.find_elements_by_class_name("clickable-row")
        column_name = rows[data_row_index].find_elements_by_tag_name("td")[0].text
        plot = self.browser.find_element_by_id("column_histogram").find_element_by_class_name("plotly")
        self.assertIsNotNone(plot)
        self.assertEqual(plot.find_element_by_class_name('xtitle').text, column_name)

    def verify_training_set_data(self, target_feature, n_splits):
        self.assertEquals(target_feature, self.browser.find_element_by_id("target_feature").text)
        splits_selector = self.browser.find_element_by_name('n_splits')
        selection = Select(splits_selector).first_selected_option.text
        self.assertEquals(n_splits, selection)

    def verify_method_data(self, training_method):
        self.assertEquals(training_method, self.browser.find_element_by_name("training_method").text)

    def verify_validation_set_data(self, validation_rows):
        self.assertEquals(validation_rows, int(self.browser.find_element_by_id("validation_rows").text))

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
