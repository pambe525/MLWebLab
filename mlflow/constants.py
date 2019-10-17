from django.conf import settings
import os.path

# Application constants
FILE_SELECT_DEFAULT = "< Choose a file >"
DATA_FILE_PATH = os.path.join(settings.BASE_DIR, "data")
FILE_SELECT_WIDGET_CLASS = "input-group-text custom-select"
CONTROL_PANEL_WIDGET_CLASS = "card-label custom-select col"
TRAINING_METHOD_CHOICES = [("Linear Regression", "Linear Regression")]
TRAINING_RATIO_CHOICES = [(0.8, "80%")]
TRAINING_METHOD_INITIAL = "Linear Regression"
TRAINING_RATIO_INITIAL = 0.8
