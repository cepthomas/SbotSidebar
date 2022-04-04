# What It Is
Commands added to the sidebar defaults. Similar in concept to SideBarEnhancements
but it has too much extra stuff. This has just the basics and can be extended incrementally.

Built for ST4 on Windows and Linux (with a couple of exceptions).


## Commands
| Command                    | Implementation | Description | Args      |
| :--------                  | :-------       | :-------    | :-------- |
| `sbot_sidebar_copy_name`   | Sidebar        | Copy file/dir name to clipboard                     |  |
| `sbot_sidebar_copy_path`   | Sidebar        | Copy full file/dir path to clipboard                |  |
| `sbot_sidebar_copy_file`   | Sidebar        | Copy selected file to a new file in the same folder |  |
| `sbot_sidebar_terminal`    | Sidebar        | Open a terminal here                                |  |
| `sbot_sidebar_open_file`   | Sidebar        | Open a file using its default application           |  |
| `sbot_sidebar_open_folder` | Sidebar        | Open a Windows Explorer here (win only)             |  |
| `sbot_sidebar_open_browser`| Sidebar        | Open html file in your browser                      |  |
| `sbot_sidebar_tree`        | Sidebar        | Run tree cmd to new view (win only)                 |  |
| `sbot_sidebar_exec`        | Sidebar        | Run selected executable with output to new view     |  |
| `sbot_sidebar_exclude`     | Sidebar        | Hide selected file/dir in project                   |  |

## Settings
No internal but the right click stuff works better with this setting:
```
"preview_on_click": "only_left",
```
