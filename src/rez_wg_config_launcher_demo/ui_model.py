from typing import Union
from rez_wg_config_launcher_demo.data_model import (
    _Setting,
    _SettingHolder,
    Configuration,
    Preset,
    Project,
)
from qtpy import QtWidgets, QtCore


class TreeConfigurationModel(QtCore.QAbstractItemModel):
    def __init__(self, root: Configuration, parent: QtWidgets.QWidget | None = None):
        super(TreeConfigurationModel, self).__init__(parent)
        self._rootItem = root

    def columnCount(self, _):
        return 1

    def data(self, index: QtCore.QModelIndex, role: int):
        if not index.isValid():
            return None

        item = index.internalPointer()
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            return item.name

        return None

    def index(self, row, column, parent):
        parentItem = self.getItem(parent)

        childItem = parentItem.children[row]

        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        item = self.getItem(index)
        parentItem: Configuration = item.parent

        if parentItem == self._rootItem:
            return QtCore.QModelIndex()

        return self.createIndex(parentItem.children.index(item), 0, parentItem)

    def getItem(self, index):
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item

        return self._rootItem

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def rowCount(self, parent):
        if not parent.isValid():
            parentItem = self._rootItem
        else:
            parentItem = parent.internalPointer()

        return len(parentItem.children)


class ConfigTableSettingModel(QtCore.QAbstractTableModel):
    def __init__(self, configuration: Union[Configuration, Preset], parent=None):
        super(ConfigTableSettingModel, self).__init__(parent)
        self.configuration: Union[Configuration] = configuration
        self.config_settings = self.configuration.get_all_configuration_settings()

    def rowCount(self, parent):
        return len(self.config_settings)

    def columnCount(self, parent):
        return 3

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            if orientation == QtCore.Qt.Orientation.Horizontal:
                if section == 0:
                    return "Inherited from"
                elif section == 1:
                    return "Setting Type"
                elif section == 2:
                    return "Setting"

    def data(self, index, role):
        if not index.isValid():
            return None

        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            config_setting = self.config_settings[index.row()]

            if index.column() == 0:
                config_name = config_setting.configuration.name
                return config_name

            elif index.column() == 1:
                setting_type = config_setting.setting.type
                return setting_type

            elif index.column() == 2:
                config_value = str(config_setting.setting)
                return config_value

        return None


class ListPresetModel(QtCore.QAbstractListModel):
    def __init__(self, project: Project, parent=None):
        super(ListPresetModel, self).__init__(parent)
        self.project: Project = project
        self.presets: list[Preset] = project.presets

    def rowCount(self, parent):
        return len(self.presets)

    def data(self, index, role):
        if not index.isValid():
            return None
        
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            preset = self.presets[index.row()]
            return preset.name

        return None
