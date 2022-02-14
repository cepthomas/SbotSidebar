import os
import subprocess
import webbrowser
import shutil
import sublime
import sublime_plugin


#-----------------------------------------------------------------------------------
def plugin_loaded():
    # print(">>> SbotSidebar plugin_loaded()")
    pass


#-----------------------------------------------------------------------------------
def plugin_unloaded():
    # print("SbotSidebar plugin_unloaded()")
    pass


#-----------------------------------------------------------------------------------
class SbotSidebarCopyNameCommand(sublime_plugin.WindowCommand):
    ''' Get file name to clipboard. '''

    def run(self, paths):
        print(paths)
        names = (os.path.split(path)[1] for path in paths)
        sublime.set_clipboard('\n'.join(names))


#-----------------------------------------------------------------------------------
class SbotSidebarCopyPathCommand(sublime_plugin.WindowCommand):
    ''' Get file path to clipboard. '''

    def run(self, paths):
        sublime.set_clipboard('\n'.join(paths))


#-----------------------------------------------------------------------------------
class SbotSidebarCopyFileCommand(sublime_plugin.WindowCommand):
    ''' Copy selected file to the same dir. '''

    def run(self, paths):
        ok = False
        fn = paths[0]
        # Find a valid file name.
        root, ext = os.path.splitext(fn)
        for i in range(1, 9):
            newfn = f'{root}_{i}{ext}'
            if not os.path.isfile(newfn):
                shutil.copyfile(fn, newfn)
                ok = True
                break

        if not ok:
            sublime.status_message("Couldn't copy file")

    def is_visible(self, paths):
        vis = len(paths) > 0 and os.path.isfile(paths[0])
        return vis


#-----------------------------------------------------------------------------------
class SbotSidebarTerminalCommand(sublime_plugin.WindowCommand):
    ''' Open term here. '''

    def run(self, paths):
        if len(paths) > 0:
            path = _get_dir(paths)
            cmd = f'wt -d "{path}"' if os.name == 'nt' else f'gnome-terminal --working-directory="{path}"'
            subprocess.run(cmd, shell=True, check=True)

    def is_visible(self, paths):
        vis = os.name == 'nt' or os.name == 'posix'
        return vis


#-----------------------------------------------------------------------------------
class SbotSidebarOpenFolderCommand(sublime_plugin.WindowCommand):
    ''' Open current folder. '''

    def run(self, paths):
        if len(paths) > 0:
            path = _get_dir(paths)
            cmd = f'explorer "{path}"' # I don't think this is simple with linux?
            subprocess.run(cmd, shell=True, check=True)

    def is_visible(self, paths):
        vis = os.name == 'nt' and len(paths) > 0
        return vis


#-----------------------------------------------------------------------------------
class SbotSidebarOpenFileCommand(sublime_plugin.WindowCommand):
    ''' Simple file opener. '''

    def run(self, paths):
        if len(paths) > 0:
            fn = f'"{paths[0]}"'
            cmd = fn if os.name == 'nt' else f'xdg-open {fn}'
            cp = subprocess.run(cmd, universal_newlines=True, shell=True)

    def is_visible(self, paths):
        vis = (os.name == 'nt' or os.name == 'posix') and len(paths) > 0
        return vis


#-----------------------------------------------------------------------------------
class SbotSidebarTreeCommand(sublime_plugin.WindowCommand):
    ''' Run tree command to clipboard. '''

    def run(self, paths):
        if len(paths) > 0:
            path = _get_dir(paths)
            cmd = f'tree "{path}" /a /f' # Linux needs this installed.
            cp = subprocess.run(cmd, universal_newlines=True, capture_output=True, shell=True, check=True)
            _create_new_view(self.window, cp.stdout)

    def is_visible(self, paths):
        vis = os.name == 'nt' and len(paths) > 0
        return vis


#-----------------------------------------------------------------------------------
class SbotSidebarExecCommand(sublime_plugin.WindowCommand):
    ''' Simple executioner for exes/cmds without args. '''

    def run(self, paths):
        if len(paths) > 0:
            path = _get_dir(paths)
            cmd = ['python', paths[0]] if paths[0].endswith('.py') else [paths[0]]
            cp = subprocess.run(cmd, universal_newlines=True, capture_output=True, shell=True, check=True, cwd=path)
            _create_new_view(self.window, cp.stdout)

    def is_visible(self, paths):
        # Assumes caller knows what they are doing.
        vis = (os.name == 'nt' or os.name == 'posix') and len(paths) > 0
        return vis


#-----------------------------------------------------------------------------------
class SbotSidebarExcludeCommand(sublime_plugin.WindowCommand):
    ''' Remove from project. Supplements builtin remove_folder. '''

    def run(self, paths):
        if len(paths) > 0:
            pdata = self.window.project_data()

            exclude = paths[0]
            path = _get_dir(paths)
            project_fn = self.window.project_file_name()

            # Locate the folder.
            found = False
            for folder in pdata["folders"]:
                folder_path = folder["path"]
                abs_path = os.path.split(project_fn)[0] if(folder_path == '.') else os.path.abspath(folder_path)

                if path.startswith(abs_path):
                    # Make a ref.
                    target_path = os.path.relpath(exclude, abs_path)
                    _, target_path = os.path.split(exclude)
                    # print(f"exclude:{exclude} abs_path:{abs_path} target_path:{target_path}")
                    patfold = "folder_exclude_patterns" if os.path.isdir(exclude) else "file_exclude_patterns"

                    try:
                        folder[patfold].append(target_path)
                    except Exception as e:
                        folder[patfold] = [target_path]
                    found = True
                    break

            # Finish up.
            if found:
                self.window.set_project_data(pdata)
            else:
                pass
                # Fails if folder moved.

    def is_visible(self, paths):
        vis = True
        # Disallow project folders - should use builtin remove_folder.
        if len(paths) > 0:
            if os.path.isdir(paths[0]):
                pdata = self.window.project_data()
                path = paths[0]
                project_fn = self.window.project_file_name()

                for folder in pdata["folders"]:
                    folder_path = folder["path"]
                    abs_path = os.path.split(project_fn)[0] if folder_path == '.' else os.path.abspath(folder_path)
                    if path == abs_path:
                        vis = False
                        break
            # else: Just a file is ok.
        else:
            vis = False

        return vis


#-----------------------------------------------------------------------------------
class SbotSidebarOpenBrowserCommand(sublime_plugin.WindowCommand):
    ''' Simple exec for html files. '''

    def run(self, paths):
        webbrowser.open_new_tab(paths[0])

    def is_visible(self, paths):
        vis = len(paths) > 0 and os.path.splitext(paths[0])[1] in ['.html', '.svg']
        return vis


#-----------------------------------------------------------------------------------
def _create_new_view(window, text):
    ''' Creates a temp view with text. Returns the view.'''
    vnew = window.new_file()
    vnew.set_scratch(True)
    vnew.run_command('append', {'characters': text})  # insert has some odd behavior - indentation
    return vnew


#-----------------------------------------------------------------------------------
def _get_dir(paths):
    path = paths[0] if os.path.isdir(paths[0]) else os.path.split(paths[0])[0]
    return path
