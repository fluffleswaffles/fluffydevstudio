import gi
import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime
import shutil

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("GtkSource", "5")

os.environ['PATH'] = os.environ.get('PATH', '')
subprocess.run(["arm-none-eabi-gcc", "--version"])

from gi.repository import Gtk, Adw, Gio, GtkSource, GLib, Pango

def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = Path(sys.executable).parent
    else:
        base_path = Path(__file__).parent
    return base_path / relative_path


GRUVBOX_DARK_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<style-scheme id="gruvbox-dark" name="Gruvbox Dark" version="1.0">
  <author>fluffles</author>
  <description>i hate everything</description>
  <color name="bg_color" value="#282828"/>
  <color name="fg_color" value="#ebdbb2"/>
  <color name="base_color" value="#3c3836"/>
  <color name="text_color" value="#ebdbb2"/>
  <color name="selected_bg_color" value="#928374"/>
  <color name="selected_fg_color" value="#282828"/>

  <color name="red" value="#cc241d"/>
  <color name="green" value="#98971a"/>
  <color name="yellow" value="#d79921"/>
  <color name="blue" value="#458588"/>
  <color name="purple" value="#b16286"/>
  <color name="aqua" value="#689d6a"/>
  <color name="orange" value="#d65d0e"/>
  <color name="gray" value="#928374"/>

  <style name="text" foreground="fg_color" background="bg_color"/>
  <style name="selection" background="selected_bg_color" foreground="selected_fg_color"/>
  <style name="cursor" foreground="fg_color"/>
  <style name="current-line-number" foreground="yellow" background="base_color"/>
  <style name="line-numbers" foreground="gray" background="base_color"/>
  <style name="current-line" background="base_color"/>
  
  <style name="def:string" foreground="green"/>
  <style name="def:comment" foreground="gray"/>
  <style name="def:number" foreground="orange"/>
  <style name="def:keyword" foreground="red" bold="true"/>
  <style name="def:type" foreground="yellow"/>
  <style name="def:preprocessor" foreground="orange"/>
  <style name="def:function" foreground="blue"/>
  <style name="def:constant" foreground="purple"/>
  <style name="def:variable" foreground="aqua"/>

  <style name="c:keyword" foreground="red" bold="true"/>
  <style name="c:type" foreground="yellow"/>
  <style name="c:string" foreground="green"/>
  <style name="c:comment" foreground="gray"/>
  <style name="c:number" foreground="orange"/>
  <style name="c:preprocessor" foreground="orange"/>
  <style name="c:function" foreground="blue"/>
</style-scheme>'''

GRUVBOX_LIGHT_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<style-scheme id="gruvbox-light" name="Gruvbox Light" version="1.0">
  <author>fluffles</author>
  <description>i hate everything 2</description>

  <color name="bg_color" value="#fbf1c7"/>
  <color name="fg_color" value="#3c3836"/>
  <color name="base_color" value="#ebdbb2"/>
  <color name="text_color" value="#3c3836"/>
  <color name="selected_bg_color" value="#928374"/>
  <color name="selected_fg_color" value="#fbf1c7"/>

  <color name="red" value="#cc241d"/>
  <color name="green" value="#98971a"/>
  <color name="yellow" value="#d79921"/>
  <color name="blue" value="#458588"/>
  <color name="purple" value="#b16286"/>
  <color name="aqua" value="#689d6a"/>
  <color name="orange" value="#d65d0e"/>
  <color name="gray" value="#928374"/>

  <style name="text" foreground="fg_color" background="bg_color"/>
  <style name="selection" background="selected_bg_color" foreground="selected_fg_color"/>
  <style name="cursor" foreground="fg_color"/>
  <style name="current-line-number" foreground="yellow" background="base_color"/>
  <style name="line-numbers" foreground="gray" background="base_color"/>
  <style name="current-line" background="base_color"/>
  
  <style name="def:string" foreground="green"/>
  <style name="def:comment" foreground="gray"/>
  <style name="def:number" foreground="orange"/>
  <style name="def:keyword" foreground="red" bold="true"/>
  <style name="def:type" foreground="yellow"/>
  <style name="def:preprocessor" foreground="orange"/>
  <style name="def:function" foreground="blue"/>
  <style name="def:constant" foreground="purple"/>
  <style name="def:variable" foreground="aqua"/>

  <style name="c:keyword" foreground="red" bold="true"/>
  <style name="c:type" foreground="yellow"/>
  <style name="c:string" foreground="green"/>
  <style name="c:comment" foreground="gray"/>
  <style name="c:number" foreground="orange"/>
  <style name="c:preprocessor" foreground="orange"/>
  <style name="c:function" foreground="blue"/>
</style-scheme>'''

class OptionsDialog(Adw.PreferencesWindow):
    def __init__(self, parent, **kwargs):
        super().__init__(**kwargs)
        self.set_transient_for(parent)
        self.set_title("Options")
        self.set_default_size(500, 400)
        self.parent = parent

        page = Adw.PreferencesPage()
        self.add(page)

        appearance_group = Adw.PreferencesGroup(title="Appearance")
        page.add(appearance_group)
        
        self.theme_row = Adw.ComboRow(title="Theme", subtitle="Choose application theme")
        self.theme_row.set_model(Gtk.StringList.new(["Dark", "Light", "Auto"]))
        
        config = self.parent.load_config()
        theme = config.get('theme', 'Dark')
        if theme == 'Dark':
            self.theme_row.set_selected(0)
        elif theme == 'Light':
            self.theme_row.set_selected(1)
        else:
            self.theme_row.set_selected(2)
        
        self.theme_row.connect("notify::selected", self.on_theme_changed)
        appearance_group.add(self.theme_row)
        
        self.color_scheme_row = Adw.ComboRow(title="Color Scheme", subtitle="Choose editor color scheme")
        
        schemes = [
            "gruvbox-dark",
            "gruvbox-light", 
            "oblivion",
            "classic",
            "tango",
            "solarized-dark",
            "solarized-light"
        ]
        self.color_scheme_row.set_model(Gtk.StringList.new(schemes))
        
        color_scheme = config.get('color_scheme', 'gruvbox-dark')
        try:
            index = schemes.index(color_scheme)
            self.color_scheme_row.set_selected(index)
        except ValueError:
            self.color_scheme_row.set_selected(0)
        
        self.color_scheme_row.connect("notify::selected", self.on_color_scheme_changed)
        appearance_group.add(self.color_scheme_row)

        stlink_group = Adw.PreferencesGroup(title="ST-Link Settings")
        page.add(stlink_group)

        self.status_row = Adw.ActionRow(title="ST-Link Status", subtitle="Checking...")
        stlink_group.add(self.status_row)

        refresh_button = Gtk.Button(label="Refresh", css_classes=["suggested-action"])
        refresh_button.connect("clicked", self.check_stlink)
        self.status_row.add_suffix(refresh_button)

        self.check_stlink(None)
    
    def on_theme_changed(self, combo, param):
        selected = combo.get_selected()
        theme_map = {0: 'Dark', 1: 'Light', 2: 'Auto'}
        theme = theme_map.get(selected, 'Dark')
        self.parent.set_theme(theme)
    
    def on_color_scheme_changed(self, combo, param):
        selected = combo.get_selected()
        if selected >= 0:
            model = combo.get_model()
            scheme_name = model.get_string(selected)
            self.parent.set_color_scheme(scheme_name)
    
    def check_stlink(self, button):
        try:
            result = subprocess.run(['lsusb'], capture_output=True, text=True)
            if 'st-link' in result.stdout.lower():
                lines = [line for line in result.stdout.split('\n') if 'st-link' in line.lower()]
                device_info = lines[0].split('ID ')[-1] if lines else "Connected"
                self.status_row.set_subtitle(f"Connected - {device_info}")
            else:
                self.status_row.set_subtitle("Not connected")
        except Exception as e:
            self.status_row.set_subtitle(f"Error: {str(e)}")

class FileExplorer(Gtk.Box):
    def __init__(self, project_path, on_file_selected):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.project_path = project_path
        self.on_file_selected = on_file_selected
        self.tree_store = Gtk.TreeStore(str, str, str)
        self.set_size_request(200, -1)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        
        self.tree_view = Gtk.TreeView(model=self.tree_store)
        self.tree_view.set_show_expanders(True)
        self.tree_view.set_enable_search(False)
        
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Files", renderer, text=0)
        self.tree_view.append_column(column)
        
        self.tree_view.connect("row-activated", self.on_row_activated)
        
        self.setup_context_menu()
        
        scrolled.set_child(self.tree_view)
        self.append(scrolled)
        
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        toolbar.set_margin_top(5)
        toolbar.set_margin_bottom(5)
        toolbar.set_margin_start(5)
        toolbar.set_margin_end(5)
        
        new_file_btn = Gtk.Button(label="New File")
        new_file_btn.connect("clicked", self.on_new_file)
        new_file_btn.set_hexpand(True)
        
        new_folder_btn = Gtk.Button(label="New Folder")
        new_folder_btn.connect("clicked", self.on_new_folder)
        new_folder_btn.set_hexpand(True)
        
        toolbar.append(new_file_btn)
        toolbar.append(new_folder_btn)
        self.append(toolbar)
        
        self.load_files()
    
    def setup_context_menu(self):
        self.popup_menu = Gio.Menu()
        
        self.popup_menu.append("Open", "explorer.open")
        self.popup_menu.append("Rename", "explorer.rename")
        self.popup_menu.append("Delete", "explorer.delete")
        
        self.actions = Gio.SimpleActionGroup()
        
        open_action = Gio.SimpleAction.new("open", None)
        open_action.connect("activate", self.on_context_open)
        self.actions.add_action(open_action)
        
        rename_action = Gio.SimpleAction.new("rename", None)
        rename_action.connect("activate", self.on_context_rename)
        self.actions.add_action(rename_action)
        
        delete_action = Gio.SimpleAction.new("delete", None)
        delete_action.connect("activate", self.on_context_delete)
        self.actions.add_action(delete_action)
        
        self.tree_view.insert_action_group("explorer", self.actions)
        
        gesture = Gtk.GestureClick.new()
        gesture.set_button(3)
        gesture.connect("pressed", self.on_gesture_pressed)
        self.tree_view.add_controller(gesture)
    
    def on_gesture_pressed(self, gesture, n_press, x, y):
        selection = self.tree_view.get_selection()
        model, iter = selection.get_selected()
        if iter:
                menu = Gtk.PopoverMenu()
                menu.set_menu_model(self.popup_menu)
                menu.set_parent(self.tree_view)
                menu.set_position(Gtk.PositionType.BOTTOM)
                menu.popup()
                return True
        return False
    
    def on_context_open(self, action, param):
        selection = self.tree_view.get_selection()
        model, iter = selection.get_selected()
        if iter:
            filepath = model.get_value(iter, 1)
            filetype = model.get_value(iter, 2)
            if filetype == "file":
                self.on_file_selected(filepath)
    
    def on_context_rename(self, action, param):
        selection = self.tree_view.get_selection()
        model, iter = selection.get_selected()
        if iter:
            old_path = model.get_value(iter, 1)
            old_name = Path(old_path).name
            
            dialog = Adw.MessageDialog(
                transient_for=self.get_root(),
                heading="Rename File",
                body=f"Enter new name for {old_name}:"
            )
            entry = Gtk.Entry()
            entry.set_text(old_name)
            entry.set_margin_top(10)
            entry.set_margin_bottom(10)
            dialog.set_extra_child(entry)
            
            dialog.add_response("cancel", "Cancel")
            dialog.add_response("rename", "Rename")
            dialog.set_response_appearance("rename", Adw.ResponseAppearance.SUGGESTED)
            
            dialog.connect("response", self.on_rename_response, old_path, iter)
            dialog.present()
    
    def on_rename_response(self, dialog, response, old_path, iter):
        if response == "rename":
            entry = dialog.get_extra_child()
            new_name = entry.get_text().strip()
            if new_name:
                new_path = str(Path(old_path).parent / new_name)
                try:
                    os.rename(old_path, new_path)
                    self.tree_store.set_value(iter, 0, new_name)
                    self.tree_store.set_value(iter, 1, new_path)
                except Exception as e:
                    error_dialog = Adw.MessageDialog(
                        transient_for=self.get_root(),
                        heading="Error",
                        body=f"Failed to rename: {str(e)}"
                    )
                    error_dialog.present()
        
        dialog.destroy()
    
    def on_context_delete(self, action, param):
        selection = self.tree_view.get_selection()
        model, iter = selection.get_selected()
        if iter:
            filepath = model.get_value(iter, 1)
            filename = Path(filepath).name
            
            dialog = Adw.MessageDialog(
                transient_for=self.get_root(),
                heading="Delete File",
                body=f"Are you sure you want to delete '{filename}'?"
            )
            
            dialog.add_response("cancel", "Cancel")
            dialog.add_response("delete", "Delete")
            dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
            
            dialog.connect("response", self.on_delete_response, filepath, iter)
            dialog.present()
    
    def on_delete_response(self, dialog, response, filepath, iter):
        if response == "delete":
            try:
                if os.path.isdir(filepath):
                    import shutil
                    shutil.rmtree(filepath)
                else:
                    os.remove(filepath)
                self.tree_store.remove(iter)
            except Exception as e:
                error_dialog = Adw.MessageDialog(
                    transient_for=self.get_root(),
                    heading="Error",
                    body=f"Failed to delete: {str(e)}"
                )
                error_dialog.present()
        
        dialog.destroy()
    
    def on_row_activated(self, treeview, path, column):
        iter = self.tree_store.get_iter(path)
        filepath = self.tree_store.get_value(iter, 1)
        filetype = self.tree_store.get_value(iter, 2)
        
        if filetype == "file":
            self.on_file_selected(filepath)
    
    def on_new_file(self, button):
        dialog = Adw.MessageDialog(
            transient_for=self.get_root(),
            heading="New File",
            body="Enter file name (with extension):"
        )
        entry = Gtk.Entry()
        entry.set_margin_top(10)
        entry.set_margin_bottom(10)
        dialog.set_extra_child(entry)
        
        dialog.add_response("cancel", "Cancel")
        dialog.add_response("create", "Create")
        dialog.set_response_appearance("create", Adw.ResponseAppearance.SUGGESTED)
        
        dialog.connect("response", self.on_new_file_response)
        dialog.present()
    
    def on_new_file_response(self, dialog, response):
        if response == "create":
            entry = dialog.get_extra_child()
            filename = entry.get_text().strip()
            if filename:
                filepath = os.path.join(self.project_path, "src", filename)
                try:
                    with open(filepath, 'w') as f:
                        f.write("")
                    self.load_files()
                    self.on_file_selected(filepath)
                except Exception as e:
                    error_dialog = Adw.MessageDialog(
                        transient_for=self.get_root(),
                        heading="Error",
                        body=f"Failed to create file: {str(e)}"
                    )
                    error_dialog.present()
        
        dialog.destroy()
    
    def on_new_folder(self, button):
        dialog = Adw.MessageDialog(
            transient_for=self.get_root(),
            heading="New Folder",
            body="Enter folder name:"
        )
        entry = Gtk.Entry()
        entry.set_margin_top(10)
        entry.set_margin_bottom(10)
        dialog.set_extra_child(entry)
        
        dialog.add_response("cancel", "Cancel")
        dialog.add_response("create", "Create")
        dialog.set_response_appearance("create", Adw.ResponseAppearance.SUGGESTED)
        
        dialog.connect("response", self.on_new_folder_response)
        dialog.present()
    
    def on_new_folder_response(self, dialog, response):
        if response == "create":
            entry = dialog.get_extra_child()
            foldername = entry.get_text().strip()
            if foldername:
                folderpath = os.path.join(self.project_path, "src", foldername)
                try:
                    os.makedirs(folderpath, exist_ok=True)
                    self.load_files()
                except Exception as e:
                    error_dialog = Adw.MessageDialog(
                        transient_for=self.get_root(),
                        heading="Error",
                        body=f"Failed to create folder: {str(e)}"
                    )
                    error_dialog.present()
        
        dialog.destroy()
    
    def load_files(self):
        self.tree_store.clear()
        src_path = os.path.join(self.project_path, "src")
        
        if os.path.exists(src_path):
            self.add_directory_to_tree(None, src_path)
    
    def add_directory_to_tree(self, parent_iter, directory):
        try:
            for item in sorted(os.listdir(directory)):
                item_path = os.path.join(directory, item)
                if os.path.isdir(item_path):
                    iter = self.tree_store.append(parent_iter, [item, item_path, "folder"])
                    self.add_directory_to_tree(iter, item_path)
                else:
                    self.tree_store.append(parent_iter, [item, item_path, "file"])
        except:
            pass
    
    def refresh(self):
        self.load_files()

class CodeEditor(Gtk.Box):
    def __init__(self, filepath=None, parent=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.filepath = filepath
        self.parent = parent
        self.modified = False
        
        self.buffer = GtkSource.Buffer()
        self.view = GtkSource.View.new_with_buffer(self.buffer)
        self.view.set_show_line_numbers(True)
        self.view.set_auto_indent(True)
        self.view.set_indent_width(4)
        self.view.set_tab_width(4)
        self.view.set_insert_spaces_instead_of_tabs(True)
        self.view.set_monospace(True)
        
        language_manager = GtkSource.LanguageManager.get_default()
        if filepath and filepath.endswith(('.c', '.h')):
            language = language_manager.get_language('c')
        elif filepath and filepath.endswith('.s'):
            language = language_manager.get_language('asm')
        elif filepath and filepath.endswith('Makefile'):
            language = language_manager.get_language('makefile')
        elif filepath and filepath.endswith('.ld'):
            language = language_manager.get_language('ld')
        else:
            language = language_manager.get_language('c')
        
        if language:
            self.buffer.set_language(language)
        
        self.apply_color_scheme()
        
        self.buffer.connect("modified-changed", self.on_modified_changed)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_child(self.view)
        scrolled.set_hexpand(True)
        scrolled.set_vexpand(True)
        
        self.append(scrolled)
        
        self.status_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.status_bar.set_margin_start(5)
        self.status_bar.set_margin_end(5)
        self.status_bar.set_margin_bottom(5)
        
        self.modified_label = Gtk.Label(label="")
        self.modified_label.add_css_class("caption")
        self.status_bar.append(self.modified_label)
        
        self.cursor_label = Gtk.Label(label="Line: 1, Column: 1")
        self.cursor_label.add_css_class("caption")
        self.cursor_label.set_halign(Gtk.Align.END)
        self.cursor_label.set_hexpand(True)
        self.status_bar.append(self.cursor_label)
        
        self.append(self.status_bar)
        
        self.buffer.connect("notify::cursor-position", self.on_cursor_position_changed)
        
        if filepath and os.path.exists(filepath):
            self.load_file(filepath)
    
    def apply_color_scheme(self):
        scheme_name = self.parent.color_scheme if self.parent else 'gruvbox-dark'
        
        manager = GtkSource.StyleSchemeManager.get_default()
        
        if scheme_name in ['gruvbox-dark', 'gruvbox-light']:
            self.apply_gruvbox_scheme(scheme_name)
        else:
            scheme = manager.get_scheme(scheme_name)
            if scheme:
                self.buffer.set_style_scheme(scheme)
            else:
                self.apply_gruvbox_scheme('gruvbox-dark')
    
    def apply_gruvbox_scheme(self, scheme_name):
        manager = GtkSource.StyleSchemeManager.get_default()
        
        scheme = manager.get_scheme(scheme_name)
        if not scheme:
            if scheme_name == 'gruvbox-dark':
                scheme_xml = GRUVBOX_DARK_XML
            else:
                scheme_xml = GRUVBOX_LIGHT_XML
            
            import tempfile
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, f"{scheme_name}.xml")
            
            try:
                with open(temp_file, 'w') as f:
                    f.write(scheme_xml)
                
                manager.append_search_path(temp_dir)
                
                scheme = manager.get_scheme(scheme_name)
                
                os.remove(temp_file)
                
                search_paths = manager.get_search_path()
                if temp_dir in search_paths:
                    search_paths = [p for p in search_paths if p != temp_dir]
            except Exception as e:
                print(f"Failed to create gruvbox scheme: {e}")
                scheme = manager.get_scheme('oblivion') or manager.get_scheme('classic')
        
        if scheme:
            self.buffer.set_style_scheme(scheme)
    
    def on_modified_changed(self, buffer):
        self.modified = buffer.get_modified()
        if self.parent:
            self.parent.update_tab_title(self)
    
    def on_cursor_position_changed(self, buffer, param):
        cursor = buffer.get_iter_at_mark(buffer.get_insert())
        line = cursor.get_line() + 1
        column = cursor.get_line_index() + 1
        self.cursor_label.set_label(f"Line: {line}, Column: {column}")
    
    def load_file(self, filepath):
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            self.buffer.set_text(content)
            self.filepath = filepath
            self.buffer.set_modified(False)
            self.modified = False
            
            try:
                mtime = os.path.getmtime(filepath)
                self.modified_time = datetime.fromtimestamp(mtime)
                self.update_modified_label()
            except:
                pass
        except Exception as e:
            print(f"Error loading file: {e}")
    
    def update_modified_label(self):
        if hasattr(self, 'modified_time'):
            time_str = self.modified_time.strftime("%Y-%m-%d %H:%M:%S")
            self.modified_label.set_label(f"Modified: {time_str}")
    
    def save(self):
        if self.filepath:
            start = self.buffer.get_start_iter()
            end = self.buffer.get_end_iter()
            text = self.buffer.get_text(start, end, False)
            
            try:
                with open(self.filepath, 'w') as f:
                    f.write(text)
                self.buffer.set_modified(False)
                self.modified = False
                
                self.modified_time = datetime.now()
                self.update_modified_label()
                return True
            except Exception as e:
                print(f"Error saving file: {e}")
                return False
        return False
    
    def save_as(self, new_path):
        self.filepath = new_path
        return self.save()

class MyWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, title="Fluffy Dev Studio")
        self.set_default_size(1200, 800)
        self.project_path = None
        self.project_name = None
        self.open_files = {}
        self.config_file = os.path.expanduser("~/.fluffy-dev-studio.json")
        
        self.config = self.load_config()
        self.color_scheme = self.config.get('color_scheme', 'gruvbox-dark')
        
        self.set_theme(self.config.get('theme', 'Dark'))
        
        actions = [
            ("newproject", self.on_new_project),
            ("openfile", self.on_open_file),
            ("openproject", self.on_open_project),
            ("saveproject", self.on_save_project),
            ("saveas", self.on_save_as),
            ("options", self.on_options),
        ]
        
        for action_name, callback in actions:
            action = Gio.SimpleAction.new(action_name, None)
            action.connect("activate", callback)
            self.add_action(action)

        outer_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        main_paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)

        self.left_pane = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.left_pane.set_size_request(250, -1)
        self.left_pane.set_visible(False)

        right_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        right_content.set_hexpand(True)

        toolbar = Adw.ToolbarView()
        header = Adw.HeaderBar()

        self.project_label = Gtk.Label(label="No project loaded")
        self.project_label.add_css_class("title-4")
        header.set_title_widget(self.project_label)

        build_button = Gtk.Button(label="Build")
        build_button.connect("clicked", self.on_build)
        build_button.set_sensitive(False)
        self.build_button = build_button

        debug_button = Gtk.Button(label="Debug")
        debug_button.connect("clicked", self.on_debug)
        debug_button.set_sensitive(False)
        self.debug_button = debug_button

        flash_button = Gtk.Button(label="Flash")
        flash_button.connect("clicked", self.on_flash)
        flash_button.set_sensitive(False)
        self.flash_button = flash_button

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        button_box.set_hexpand(False)
        button_box.set_homogeneous(True)
        button_box.append(build_button)
        button_box.append(debug_button)
        button_box.append(flash_button)
        header.pack_start(button_box)
        
        toolbar.add_top_bar(header)
        outer_box.append(toolbar)

        menu_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        menu_bar.add_css_class("menubar")

        file_menu_button = Gtk.MenuButton(label="File")
        file_menu_button.add_css_class("flat")
        file_menu = Gio.Menu()
        file_menu.append("New Project", "win.newproject")
        file_menu.append("Open Project", "win.openproject")
        file_menu.append("Open File", "win.openfile")
        file_menu.append("Save", "win.saveproject")
        file_menu.append("Save As", "win.saveas")
        file_menu_button.set_menu_model(file_menu)
        menu_bar.append(file_menu_button)

        window_menu_button = Gtk.MenuButton(label="Window")
        window_menu_button.add_css_class("flat")
        window_menu = Gio.Menu()
        window_menu.append("Options", "win.options")
        window_menu.append("About", "app.about")
        window_menu_button.set_menu_model(window_menu)
        menu_bar.append(window_menu_button)
        
        outer_box.append(menu_bar)

        self.notebook = Gtk.Notebook()
        self.notebook.set_scrollable(True)
        self.notebook.connect("page-added", self.on_tab_added)
        self.notebook.connect("page-removed", self.on_tab_removed)
        self.notebook.connect("page-reordered", self.on_tab_reordered)
        self.notebook.connect("switch-page", self.on_tab_switched)
        right_content.append(self.notebook)

        main_paned.set_start_child(self.left_pane)
        main_paned.set_end_child(right_content)
        try:
            main_paned.set_position(300)
        except Exception:
            pass

        def _clamp_paned(paned, pspec):
            try:
                pos = paned.get_position()
                min_pos = 150
                alloc = self.get_allocated_width()
                if alloc and alloc > 0:
                    max_pos = min(max(400, alloc // 2), alloc - 200)
                else:
                    max_pos = 800
                if pos < min_pos:
                    paned.set_position(min_pos)
                elif pos > max_pos:
                    paned.set_position(max_pos)
            except Exception:
                pass

        main_paned.connect("notify::position", _clamp_paned)

        outer_box.append(main_paned)
        self.set_content(outer_box)
        
        self.connect("close-request", self.on_window_close)
    
    def load_config(self):
        config = {'theme': 'Dark', 'color_scheme': 'gruvbox-dark'}
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
        except:
            pass
        return config
    
    def save_config(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f)
        except:
            pass
    
    def set_theme(self, theme):
        self.config['theme'] = theme
        self.save_config()
        
        style_manager = Adw.StyleManager.get_default()
        if theme == 'Dark':
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        elif theme == 'Light':
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
        else:
            style_manager.set_color_scheme(Adw.ColorScheme.DEFAULT)
    
    def set_color_scheme(self, scheme_name):
        self.config['color_scheme'] = scheme_name
        self.save_config()
        self.color_scheme = scheme_name
        
        for editor in self.open_files.values():
            editor.apply_color_scheme()
    
    def on_tab_added(self, notebook, child, page_num):
        tab_box = Gtk.Box(spacing=5)
        label = Gtk.Label(label=self.get_tab_title(child))
        close_button = Gtk.Button.new_from_icon_name("window-close-symbolic")
        close_button.add_css_class("flat")
        close_button.set_size_request(20, 20)
        close_button.connect("clicked", self.on_close_tab, child)
        
        tab_box.append(label)
        tab_box.append(close_button)
        
        notebook.set_tab_label(child, tab_box)
    
    def on_tab_removed(self, notebook, child, page_num):
        if child.filepath in self.open_files:
            del self.open_files[child.filepath]
    
    def on_tab_reordered(self, notebook, child, page_num):
        pass
    
    def on_tab_switched(self, notebook, page, page_num):
        pass
    
    def on_close_tab(self, button, editor):
        if editor.modified:
            dialog = Adw.MessageDialog(
                transient_for=self,
                heading="Save Changes?",
                body=f"Save changes to {os.path.basename(editor.filepath)}?"
            )
            dialog.add_response("cancel", "Cancel")
            dialog.add_response("discard", "Don't Save")
            dialog.add_response("save", "Save")
            dialog.set_response_appearance("save", Adw.ResponseAppearance.SUGGESTED)
            dialog.set_response_appearance("discard", Adw.ResponseAppearance.DESTRUCTIVE)
            
            dialog.connect("response", self.on_close_tab_response, editor)
            dialog.present()
        else:
            self.close_tab(editor)
    
    def on_close_tab_response(self, dialog, response, editor):
        if response == "save":
            if editor.save():
                self.close_tab(editor)
        elif response == "discard":
            self.close_tab(editor)
        dialog.destroy()
    
    def close_tab(self, editor):
        page_num = self.notebook.page_num(editor)
        if page_num >= 0:
            self.notebook.remove_page(page_num)
    
    def get_tab_title(self, editor):
        if editor.filepath:
            name = os.path.basename(editor.filepath)
            if editor.modified:
                return f"{name} *"
            return name
        return "Untitled"
    
    def update_tab_title(self, editor):
        page_num = self.notebook.page_num(editor)
        if page_num >= 0:
            tab_label = self.notebook.get_tab_label(editor)
            if tab_label and isinstance(tab_label, Gtk.Box):
                label = tab_label.get_first_child()
                if label and isinstance(label, Gtk.Label):
                    label.set_label(self.get_tab_title(editor))
    
    def open_file_in_editor(self, filepath):
        if filepath in self.open_files:
            page = self.open_files[filepath]
            self.notebook.set_current_page(self.notebook.page_num(page))
            return

        editor = CodeEditor(filepath, self)
        self.notebook.append_page(editor, Gtk.Label(label=os.path.basename(filepath)))
        self.notebook.set_current_page(self.notebook.get_n_pages() - 1)
        self.open_files[filepath] = editor
    
    def save_all_files(self):
        for editor in self.open_files.values():
            editor.save()
    
    def on_new_project(self, action, param):
        dialog = Gtk.FileChooserDialog(
            title="Create New Project",
            transient_for=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER
        )
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Create", Gtk.ResponseType.OK)
        
        dialog.connect("response", self._on_new_project_response)
        dialog.present()
    
    def _on_new_project_response(self, dialog, response_id):
        if response_id == Gtk.ResponseType.OK:
            file = dialog.get_file()
            if file:
                folder = file.get_path()
                project_name = os.path.basename(folder.rstrip('/'))

                self.create_project_structure(folder, project_name)

                self.load_project(folder, project_name)
        
        dialog.destroy()
    
    def create_project_structure(self, folder, project_name):
        core_path = get_resource_path("core")

        if not core_path.exists():
            dialog = Adw.AlertDialog(
                title="Core Missing",
                body=f"Core template folder not found:\n{core_path}",
                close_response="ok"
            )
            dialog.present(self)
            return

        try:
            for item in core_path.iterdir():
                src = item
                dst = Path(folder) / item.name

                if src.is_dir():
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)

            makefile_path = Path(folder) / "Makefile"
            if makefile_path.exists():
                content = makefile_path.read_text()
                content = content.replace("{{PROJECT_NAME}}", project_name)
                makefile_path.write_text(content)

        except Exception as e:
            dialog = Adw.AlertDialog(
                title="Project Creation Failed",
                body=str(e),
                close_response="ok"
            )
            dialog.present(self)
    
    def load_project(self, folder, project_name):
        self.project_path = folder
        self.project_name = project_name
        self.project_label.set_label(f"Project: {project_name}")

        self.build_button.set_sensitive(True)
        self.debug_button.set_sensitive(True)
        self.flash_button.set_sensitive(True)

        while self.notebook.get_n_pages() > 0:
            self.notebook.remove_page(0)
        self.open_files.clear()

        self.update_file_explorer()

        main_files = [
            os.path.join(folder, "src", "main.c"),
            os.path.join(folder, "Makefile"),
        ]
        
        for file in main_files:
            if os.path.exists(file):
                self.open_file_in_editor(file)
    
    def update_file_explorer(self):
        for child in self.left_pane:
            self.left_pane.remove(child)
        
        if self.project_path:
            self.file_explorer = FileExplorer(self.project_path, self.on_file_selected_from_explorer)
            self.left_pane.append(self.file_explorer)
            self.left_pane.set_visible(True)
        else:
            self.left_pane.set_visible(False)
    
    def on_file_selected_from_explorer(self, filepath):
        self.open_file_in_editor(filepath)
    
    def on_open_project(self, action, param):
        dialog = Gtk.FileChooserDialog(
            title="Open Project",
            transient_for=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER
        )
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Open", Gtk.ResponseType.OK)
        
        dialog.connect("response", self._on_open_project_response)
        dialog.present()
    
    def _on_open_project_response(self, dialog, response_id):
        if response_id == Gtk.ResponseType.OK:
            file = dialog.get_file()
            if file:
                folder = file.get_path()
                project_name = os.path.basename(folder.rstrip('/'))

                makefile = os.path.join(folder, "Makefile")
                src_dir = os.path.join(folder, "src")
                
                if os.path.exists(makefile) and os.path.exists(src_dir):
                    self.load_project(folder, project_name)
                else:
                    dialog_error = Adw.AlertDialog(
                        title="Invalid Project",
                        body="Selected folder does not contain a valid project structure.",
                        close_response="ok"
                    )
                    dialog_error.present(self)
        
        dialog.destroy()
    
    def on_open_file(self, action, param):
        dialog = Gtk.FileChooserDialog(
            title="Open File",
            transient_for=self,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Open", Gtk.ResponseType.OK)
        
        filter_text = Gtk.FileFilter()
        filter_text.set_name("Source files")
        filter_text.add_pattern("*.c")
        filter_text.add_pattern("*.h")
        filter_text.add_pattern("*.s")
        filter_text.add_pattern("*.ld")
        filter_text.add_pattern("Makefile")
        dialog.add_filter(filter_text)
        
        filter_any = Gtk.FileFilter()
        filter_any.set_name("All files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)
        
        dialog.connect("response", self._on_open_file_response)
        dialog.present()
    
    def _on_open_file_response(self, dialog, response_id):
        if response_id == Gtk.ResponseType.OK:
            file = dialog.get_file()
            if file:
                filepath = file.get_path()
                if os.path.exists(filepath):
                    self.open_file_in_editor(filepath)
        
        dialog.destroy()
    
    def on_save_project(self, action, param):
        self.save_all_files()
        if hasattr(self, 'file_explorer'):
            self.file_explorer.refresh()
    
    def on_save_as(self, action, param):
        current_page = self.notebook.get_current_page()
        if current_page >= 0:
            editor = self.notebook.get_nth_page(current_page)
            if editor and editor.filepath:
                dialog = Gtk.FileChooserDialog(
                    title="Save File As",
                    transient_for=self,
                    action=Gtk.FileChooserAction.SAVE
                )
                dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
                dialog.add_button("Save", Gtk.ResponseType.OK)
                
                dialog.set_current_name(os.path.basename(editor.filepath))
                
                if self.project_path:
                    dialog.set_current_folder(os.path.join(self.project_path, "src"))
                
                dialog.connect("response", self._on_save_as_response, editor)
                dialog.present()
    
    def _on_save_as_response(self, dialog, response_id, editor):
        if response_id == Gtk.ResponseType.OK:
            file = dialog.get_file()
            if file:
                new_path = file.get_path()
                if editor.save_as(new_path):
                    if editor.filepath in self.open_files:
                        del self.open_files[editor.filepath]
                    self.open_files[new_path] = editor
                    
                    self.update_tab_title(editor)
                    
                    if hasattr(self, 'file_explorer'):
                        self.file_explorer.refresh()
        
        dialog.destroy()
    
    def on_options(self, action, param):
        dialog = OptionsDialog(self)
        dialog.present()
    
    def on_build(self, button):
        if not self.project_path:
            return

        self.save_all_files()

        try:
            result = subprocess.run(
                ['make', 'all'],
                cwd=self.project_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                dialog = Adw.AlertDialog(
                    title="Build Successful",
                    body="Project built successfully!\n\nCheck build/ directory for output files.",
                    close_response="ok"
                )
            else:
                error_msg = result.stderr if result.stderr else result.stdout
                dialog = Adw.AlertDialog(
                    title="Build Failed",
                    body=f"Build failed with error:\n\n{error_msg}",
                    close_response="ok"
                )
        except Exception as e:
            dialog = Adw.AlertDialog(
                title="Build Error",
                body=f"Error during build: {str(e)}",
                close_response="ok"
            )
        
        dialog.present(self)
    
    def on_debug(self, button):
        print("Debug clicked - Not implemented yet")
    
    def on_flash(self, button):
        if not self.project_path:
            return
        try:
            result = subprocess.run(['lsusb'], capture_output=True, text=True)
            if 'st-link' not in result.stdout.lower():
                dialog = Adw.AlertDialog(
                    title="ST-Link Not Found",
                    body="ST-Link device not detected. Please connect your ST-Link and try again.",
                    close_response="ok"
                )
                dialog.present(self)
                return
        except:
            pass

        self.save_all_files()
        
        try:
            result = subprocess.run(
                ['make', 'flash'],
                cwd=self.project_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                dialog = Adw.AlertDialog(
                    title="Flash Successful",
                    body="Firmware flashed successfully!",
                    close_response="ok"
                )
            else:
                error_msg = result.stderr if result.stderr else result.stdout
                dialog = Adw.AlertDialog(
                    title="Flash Failed",
                    body=f"Flash failed with error:\n\n{error_msg}",
                    close_response="ok"
                )
        except Exception as e:
            dialog = Adw.AlertDialog(
                title="Flash Error",
                body=f"Error during flash: {str(e)}",
                close_response="ok"
            )
        
        dialog.present(self)
    
    def on_window_close(self, window):
        unsaved_files = []
        for editor in self.open_files.values():
            if editor.modified:
                unsaved_files.append(os.path.basename(editor.filepath))
        
        if unsaved_files:
            dialog = Adw.MessageDialog(
                transient_for=self,
                heading="Unsaved Changes",
                body=f"You have unsaved changes in {len(unsaved_files)} file(s).\n\nSave changes before closing?"
            )
            dialog.add_response("cancel", "Cancel")
            dialog.add_response("discard", "Don't Save")
            dialog.add_response("save", "Save All")
            dialog.set_response_appearance("save", Adw.ResponseAppearance.SUGGESTED)
            dialog.set_response_appearance("discard", Adw.ResponseAppearance.DESTRUCTIVE)
            
            def on_close_response(dialog, response):
                if response == "save":
                    self.save_all_files()
                    self.get_application().quit()
                elif response == "discard":
                    self.get_application().quit()
                dialog.destroy()
            
            dialog.connect("response", on_close_response)
            dialog.present()
            return True
        
        return False

class MyApplication(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.fluffles.fluffydevelopment")

        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self.on_about)
        self.add_action(about_action)
    
    def on_about(self, action, param):
        about = Adw.AboutWindow(
            transient_for=self.get_active_window(),
            application_name="fluffy stm32 development",
            application_icon="application-x-executable",
            developer_name="fluffles",
            version="0.0.1",
            developers=["fluffles"],
            copyright="© 2026 fluffles",
            license_type=Gtk.License.MIT_X11,
            website="https://fluffywaffles.space/"
        )
        about.present()
    
    def do_activate(self):
        win = MyWindow(application=self)
        win.present()

if __name__ == "__main__":
    app = MyApplication()
    app.run(None)