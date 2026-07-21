from actions import (
    open_app,
    close_app,
    open_file,
    open_folder,
    search_files,
    quick_search_files,
    find_installed_app,
    delete_file,
    copy_file,
    move_file,
)


def register_tools(registry):

    registry.register(
        "open_app",
        open_app,
    )

    registry.register(
        "close_app",
        close_app,
    )

    registry.register(
        "find_installed_app",
        find_installed_app,
    )

    registry.register(
        "quick_search_files",
        quick_search_files,
    )

    registry.register(
        "search_files",
        search_files,
    )

    registry.register(
        "open_file",
        open_file,
    )

    registry.register(
        "open_folder",
        open_folder,
    )

    registry.register(
        "delete_file",
        delete_file,
    )

    registry.register(
        "copy_file",
        copy_file,
    )

    registry.register(
        "move_file",
        move_file,
    )