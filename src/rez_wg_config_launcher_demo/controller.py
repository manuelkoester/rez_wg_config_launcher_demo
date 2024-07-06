from rez_wg_config_launcher_demo.data_model import Configuration
from rez_wg_config_launcher_demo import ui_model


def create_config_tree_model_from_root_config(
    root: Configuration,
) -> ui_model.TreeConfigurationModel:
    return ui_model.TreeConfigurationModel(root)
