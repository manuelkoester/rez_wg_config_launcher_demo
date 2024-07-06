from rez_wg_config_launcher_demo.data_model import (
    Configuration,
    EnvVarAction,
    Preset,
    Project,
)
from rez_wg_config_launcher_demo import view
from qtpy.QtWidgets import QApplication


def create_config_data() -> Configuration:
    root = Configuration("root")

    studio = (
        Configuration("studio")
        .set_parent_configuration(root)
        .add_env_var("STUDIO", "rez_studios", EnvVarAction.SET)
        .add_env_var("STUDIO_SHORT", "rs", EnvVarAction.SET)
        .add_env_var("TIMEZONE", "PST", EnvVarAction.SET)
        .add_env_var("LANGUAGE", "en_US", EnvVarAction.SET)
        .add_icon("rez.png")
    )

    applications = Configuration("applications").set_parent_configuration(studio)
    maya_base: Configuration = (
        Configuration("maya")
        .set_parent_configuration(applications)
        .add_icon("maya.png")
        .add_tool("maya")
        .add_package_requirement("maya", "~=2022")
        .add_package_requirement("rs_maya", "~=1.0.0")
    )
    houdini_base: Configuration = (
        Configuration("houdini")
        .set_parent_configuration(applications)
        .add_icon("houdini.png")
        .add_tool("houdini")
        .add_package_requirement("houdini", "~=20.5")
        .add_package_requirement("rs_houdini", ">=5.1.0")
        .add_package_requirement("sidefx_labs", "~=20.5")
    )
    houdini_fx: Configuration = (
        Configuration("houdini_fx")
        .set_parent_configuration(houdini_base)
        .add_package_requirement("axiom_houdini", "~=1.0.0")
        .add_tool("houdinifx")
    )

    projects: Configuration = Configuration("projects").set_parent_configuration(studio)
    my_big_project_A: Configuration = (
        Configuration("my_big_project_A")
        .set_parent_configuration(projects)
        .add_env_var("PROJECT", "my_big_project_A", EnvVarAction.SET)
        .add_env_var("PROJECT_SHORT", "mbpa", EnvVarAction.SET)
        .add_env_var("FPS", "24", EnvVarAction.SET)
        .add_env_var("RESOLUTION", "1920x1080", EnvVarAction.SET)
    )
    my_little_project_B: Configuration = (
        Configuration("my_little_project_B")
        .set_parent_configuration(projects)
        .add_env_var("PROJECT", "my_little_project_B", EnvVarAction.SET)
        .add_env_var("PROJECT_SHORT", "mlpb", EnvVarAction.SET)
        .add_env_var("FPS", "30", EnvVarAction.SET)
        .add_env_var("RESOLUTION", "1280x720", EnvVarAction.SET)
    )
    mbpa_houdini_base: Configuration = (
        Configuration("mbpa_houdini_base")
        .set_parent_configuration(my_big_project_A)
        .add_inheriting_configuration(houdini_fx)
        .add_package_requirement("qlib", "~=1.0.0")
        .add_package_requirement("rs_houdini", "~=4.0.0")
        .add_package_requirement("houdini", "~=20.0.0")
        .add_package_requirement("sidefx_labs", "")
    )
    mbpa_houdini_vegetation: Configuration = (
        Configuration("mbpa_houdini_vegetation")
        .set_parent_configuration(mbpa_houdini_base)
        .add_inheriting_configuration(houdini_base)
        .add_package_requirement("qlib", "~=5.0.0")
    )
    mbpa_maya_base: Configuration = (
        Configuration("mbpa_maya_base")
        .set_parent_configuration(my_big_project_A)
        .add_inheriting_configuration(maya_base)
    )

    mlpb_houdini_base: Configuration = (
        Configuration("mlpb_houdini_base")
        .set_parent_configuration(my_little_project_B)
        .add_inheriting_configuration(houdini_fx)
        .add_package_requirement("mlbp_houdini", "~=3.0.0")
    )
    mlpb_maya_base: Configuration = (
        Configuration("mlpb_maya_base")
        .set_parent_configuration(my_little_project_B)
        .add_inheriting_configuration(maya_base)
    )
    return root


def create_project_data(root_config: Configuration) -> list[Project]:
    projects = []
    mbpa: Project = Project("my_big_project_A", "mbpa")
    mlpb: Project = Project("my_little_project_B", "mlpb")

    mbpa_houdini_vegetation_dev: Preset = (
        Preset(
            "Houdini Vegetation dev ⚒",
            root_config.get_child_by_name("mbpa_houdini_vegetation"),
        )
        .add_env_var("HOUDINI_OTLSCAN_PATH", "/path/to/test/otls", EnvVarAction.PREPEND)
        .add_env_var(
            "REZ_PACKAGES_PATH", "/path/to/test/packages", EnvVarAction.PREPEND
        )
        .add_package_requirement("my_speedtree_importer", "~=1.0.0")
    )

    mbpa_houdini_vegetation_prod: Preset = Preset(
        "Houdini Vegetation 🌲",
        root_config.get_child_by_name("mbpa_houdini_vegetation"),
    ).add_icon("cool_tree.png")

    mbpa_maya_rigging_dev: Preset = (
        Preset(
            "Maya Rigging",
            root_config.get_child_by_name("maya"),
        )
        .add_package_requirement("mgear", "~=3.0.0")
        .add_env_var(
            "REZ_PACKAGES_PATH", "/path/to/test/packages", EnvVarAction.PREPEND
        )
        .add_env_var("MAYA_SCRIPT_PATH", "/path/to/test/scripts", EnvVarAction.PREPEND)
        .add_env_var("TESTING", "1", EnvVarAction.SET)
    )

    mlpb_houdini_fx: Preset = Preset(
        "Houdini FX",
        root_config.get_child_by_name("mlpb_houdini_base"),
    ).add_icon("cool_fx.png")\
        .add_env_var("HOUDINI_OTLSCAN_PATH", "/path/to/test/otls", EnvVarAction.PREPEND)\
        .add_package_requirement("my_fx_tools", "~=1.0.0")
    
    mlpb_maya_characters: Preset = Preset(
        "Maya Characters",
        root_config.get_child_by_name("mlpb_maya_base"),
    ).add_icon("cool_character.png")\
        .add_package_requirement("mgear", "~=3.0.0")

    # fmt: off
    mbpa\
        .add_preset(mbpa_houdini_vegetation_dev)\
        .add_preset(mbpa_houdini_vegetation_prod)\
        .add_preset(mbpa_maya_rigging_dev)
    
    mlpb\
        .add_preset(mlpb_houdini_fx)\
        .add_preset(mlpb_maya_characters)
    # fmt: on

    projects.append(mbpa)
    projects.append(mlpb)
    return projects

def run():
    root = create_config_data()
    projects = create_project_data(root)

    app = QApplication([])
    launcher = view.AppLauncher(projects, root)
    launcher.show()

    app.exec_()

if __name__ == "__main__":
    run()