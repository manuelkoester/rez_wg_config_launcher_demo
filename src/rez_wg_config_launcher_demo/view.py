from typing import Optional
from qtpy import QtWidgets, QtCore

from rez_wg_config_launcher_demo.data_model import Configuration, Preset, Project
from rez_wg_config_launcher_demo import ui_model, controller


class InspectPathTree(QtWidgets.QTreeView):
    def __init__(self, parent=None):
        super(InspectPathTree, self).__init__()

        self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.setAlternatingRowColors(True)
        self.setHeaderHidden(True)


class ConfigurationTable(QtWidgets.QTableView):
    def __init__(self, parent=None):
        super(ConfigurationTable, self).__init__()

        self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.setAlternatingRowColors(True)
        self.setSizeAdjustPolicy(
            QtWidgets.QAbstractItemView.SizeAdjustPolicy.AdjustToContents
        )
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)


class PresetList(QtWidgets.QListView):
    def __init__(self, parent=None, project=None):
        super(PresetList, self).__init__()

        self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.setAlternatingRowColors(True)
        self.setModel(ui_model.ListPresetModel(project))
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.preset_editor: Optional[PresetEditor] = None

    def show_context_menu(self, position: QtCore.QPoint):
        context_menu = QtWidgets.QMenu(self)

        action_edit = QtWidgets.QAction("Edit Preset", self)
        action_edit.triggered.connect(self.show_preset_editor)

        context_menu.addAction(action_edit)
        context_menu.exec(self.viewport().mapToGlobal(position))

    def show_preset_editor(self):
        selected_index = self.selectedIndexes()[0]
        preset = selected_index.model().presets[selected_index.row()]
        
        self.preset_settings_list = PresetEditor(preset=preset)
        self.preset_settings_list.show()


class AppLauncher(QtWidgets.QMainWindow):
    def __init__(self, projects: list[Project], root_config: Configuration):
        super(AppLauncher, self).__init__()
        self.resize(800, 800)
        self.setWindowTitle("App Launcher")

        self.projects = projects
        self.current_project = self.projects[0]

        self.main_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.main_widget)
        main_layout = QtWidgets.QVBoxLayout()
        self.main_widget.setLayout(main_layout)

        # Widgets
        self.project_label = QtWidgets.QLabel(
            f"Current Project : '{self.current_project.name}'"
        )
        self.project_combo = QtWidgets.QComboBox()
        # main_layout.addWidget(self.project_label)
        main_layout.addWidget(self.project_combo)

        self.project_combo.addItems([project.name for project in self.projects])
        self.project_combo.currentIndexChanged.connect(self.on_project_changed)

        self.preset_list_view = PresetList(self, self.current_project)
        main_layout.addWidget(self.preset_list_view)

        # Config editor
        self.root_config = root_config
        self.config_editor = ConfigEditor(self.root_config)

        # Menu Bar
        self.edit_menu = self.menuBar().addMenu("&Edit")
        open_config_editor = QtWidgets.QAction("Open Config Editor", self)
        open_config_editor.triggered.connect(self.open_config_editor)
        self.edit_menu.addAction(open_config_editor)

    def open_config_editor(self):
        self.config_editor.show()
    
    def on_project_changed(self, index):
        self.current_project = self.projects[index]
        self.preset_list_view.setModel(ui_model.ListPresetModel(self.current_project))


class PresetEditor(QtWidgets.QWidget):
    def __init__(self, preset: Preset, parent=None):
        super(PresetEditor, self).__init__(parent)
        self.setWindowTitle("Preset Editor")

        self.resize(600, 600)

        main_layout = QtWidgets.QHBoxLayout()
        self.setLayout(main_layout)
    
        self.configuration_table_view = ConfigurationTable(self)
        list_model = ui_model.ConfigTableSettingModel(preset)
        self.set_table_setting_model(list_model)

        main_layout.addWidget(self.configuration_table_view)

    def set_table_setting_model(self, model: ui_model.ConfigTableSettingModel):
        self.configuration_table_view.setModel(model)


class ConfigEditor(QtWidgets.QWidget):
    def __init__(self, root_config: Configuration, parent=None):
        super(ConfigEditor, self).__init__(parent)
        self.setWindowTitle("Config Editor")

        self.resize(1000, 600)

        main_layout = QtWidgets.QHBoxLayout()
        self.setLayout(main_layout)

        self.config_tree_view = InspectPathTree(self)
        root = Configuration("root")
        model = controller.create_config_tree_model_from_root_config(root)
        self.set_tree_model(model)

        self.configuration_table_view = ConfigurationTable(self)
        table_model = ui_model.ConfigTableSettingModel(root)
        self.set_table_setting_model(table_model)

        main_layout.addWidget(self.config_tree_view)
        main_layout.addWidget(self.configuration_table_view)

        config_tree_model = controller.create_config_tree_model_from_root_config(
            root_config
        )
        self.set_tree_model(config_tree_model)
        # Connect selectionChanged signal to an intermediary function

    def set_tree_model(self, model: ui_model.TreeConfigurationModel):
        self.config_tree_view.setModel(model)
        self.config_tree_view.selectionModel().selectionChanged.connect(
            self.on_selection_changed
        )
        self.config_tree_view.expandAll()

    def set_table_setting_model(self, model: ui_model.ConfigTableSettingModel):
        self.configuration_table_view.setModel(model)

    def on_selection_changed(self, selected, deselected):
        if not selected.indexes():
            root = Configuration("root")
            model = ui_model.ConfigTableSettingModel(root)
            self.set_table_setting_model(model)
            return

        selected_id = selected.indexes()[0]
        item = selected_id.internalPointer()

        model = ui_model.ConfigTableSettingModel(configuration=item)
        self.set_table_setting_model(model)
