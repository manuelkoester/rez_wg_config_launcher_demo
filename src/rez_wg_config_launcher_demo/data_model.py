from dataclasses import dataclass, field
from enum import Enum
import os
from typing import Any, Generator, Optional, Self
import abc


class EnvVarAction(Enum):
    APPEND = 0
    PREPEND = 1
    SET = 2


@dataclass
class _Setting:
    pass


@dataclass
class EnvVar(_Setting):
    key: str
    value: str
    action: EnvVarAction
    type: str = "Environment Variable"

    def __repr__(self) -> str:
        return f"{self.key}: {self.value} ({self.action.name})"


@dataclass
class PackageRequirement(_Setting):
    package_name: str
    version_specifier: str
    type: str = "Package Requirement"

    def __repr__(self) -> str:
        return f"{self.package_name}{self.version_specifier}"


@dataclass
class Icon(_Setting):
    icon: os.PathLike | str
    type: str = "Icon"

    def __repr__(self) -> str:
        return f"{self.icon}"


@dataclass
class Tool(_Setting):
    name: str
    type: str = "Tool"

    def __repr__(self) -> str:
        return f"{self.name}"


@dataclass
class _SettingHolder:
    name: str

    def add_env_var(self, key: str, value: str, action: EnvVarAction):
        self.settings.append(EnvVar(key, value, action))  # type: ignore[attr-defined]
        return self

    def add_package_requirement(self, package_name: str, version_specifier: str):
        self.settings.append(PackageRequirement(package_name, version_specifier))  # type: ignore[attr-defined]
        return self

    def add_icon(self, icon: os.PathLike | str):
        self.settings.append(Icon(icon))  # type: ignore[attr-defined]
        return self

    def add_tool(self, name: str):
        self.settings.append(Tool(name))  # type: ignore[attr-defined]
        return self


@dataclass
class Configuration(_SettingHolder):
    parent: Optional[Self] = None
    children: list[Self] = field(default_factory=lambda: [])
    inherits: list[Self] = field(default_factory=lambda: [])
    settings: list[_Setting] = field(default_factory=lambda: [])

    def get_all_configuration_settings(self):
        all_configuration_settings: list[ConfigurationSetting] = []
        previous_settings: list[_Setting] = []
        for config in self.parents_inherits_self_generator():
            for setting in config.settings:
                if setting not in previous_settings:
                    previous_settings.append(setting)
                    all_configuration_settings.append(
                        ConfigurationSetting(setting, config)
                    )
        return all_configuration_settings

    def add_inheriting_configuration(self, inherits: Self):
        self.inherits.append(inherits)
        return self

    def add_child_configuration(self, child: Self):
        self.children.append(child)
        child.parent = self
        return self

    def set_parent_configuration(self, parent: Self):
        parent.children.append(self)
        self.parent = parent
        return self

    def parents_inherits_self_generator(
        self, inherit_parents: bool = True, root: bool = True
    ):
        if self.parent:
            yield from self.parent.parents_inherits_self_generator(root=False)
            yield self.parent

        if root or inherit_parents:
            for inherit in self.inherits:
                yield inherit
        if root:
            yield self

    def child_generator(self, root: bool = True):
        if root:
            yield self

        for child in self.children:
            yield child
            yield from child.child_generator(root=False)

    def get_child_by_name(self, name: str) -> Optional[Self]:
        for child in self.child_generator():
            if child.name == name:
                return child
        return None

@dataclass
class ConfigurationSetting:
    setting: _Setting
    configuration: _SettingHolder


@dataclass
class Preset(_SettingHolder):
    base_configuration: Configuration
    settings: list[_Setting] = field(default_factory=lambda: [])

    def configuration_preset_generator(self, inherit_parents: bool = True) -> Generator[_SettingHolder, Any, Any]:
        yield from self.base_configuration.parents_inherits_self_generator(
            root=False, inherit_parents=inherit_parents
        )
        yield self
    
    
    def get_all_configuration_settings(self):
        all_configuration_settings: list[ConfigurationSetting] = []
        previous_settings: list[_Setting] = []
        for config in self.configuration_preset_generator():
            setting: _Setting
            for setting in config.settings:
                if setting not in previous_settings:
                    previous_settings.append(setting)
                    all_configuration_settings.append(
                        ConfigurationSetting(setting, config)
                    )
        return all_configuration_settings


@dataclass
class Project:
    name: str
    short_name: str
    presets: list[Preset] = field(default_factory=lambda: [])

    def add_preset(self, preset: Preset):
        self.presets.append(preset)
        return self
