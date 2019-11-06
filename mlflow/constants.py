import os.path

from django.conf import settings

# Application constants
FILE_SELECT_DEFAULT = "< Choose a file >"
DATA_FILE_PATH = os.path.join(settings.BASE_DIR, "data")
FILE_SELECT_WIDGET_CLASS = "custom-select bg-dark text-white h5 select-override"
CONTROL_PANEL_WIDGET_CLASS = "card-label custom-select"
TRAINING_METHOD_CHOICES = [("Linear Regression", "Linear Regression")]
SPLITS_CHOICES = [(2, 2), (3, 3), (4, 4), (5, 5), (10, 10)]
TRAINING_METHOD_INITIAL = "Linear Regression"
SPLITS_INITIAL = 5
