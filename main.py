import os
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox, simpledialog
import time
import zipfile


class AdvancedFileExplorer:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced File Explorer")
        self.root.geometry("1000x600")

        self.current_path = os.getcwd()

        self.create_widgets()

    def create_widgets(self):
        self.toolbar = ttk.Frame(self.root)
        self.toolbar.pack(side=TOP, fill=X)

        ttk.Button(self.toolbar, text="Open Folder", command=self.open_folder, bootstyle="danger").pack(side=LEFT, padx=5)
        self.search_entry = ttk.Entry(self.toolbar, width=30)
        self.search_entry.pack(side=LEFT, padx=5)
        ttk.Button(self.toolbar, text="Search", command=self.search_files, bootstyle="danger").pack(side=LEFT, padx=5)
        ttk.Button(self.toolbar, text="Create Folder", command=self.create_folder, bootstyle="danger").pack(side=LEFT, padx=5)
        ttk.Button(self.toolbar, text="Delete", command=self.delete_item, bootstyle="danger").pack(side=LEFT, padx=5)
        ttk.Button(self.toolbar, text="Rename", command=self.rename_item, bootstyle="danger").pack(side=LEFT, padx=5)
        ttk.Button(self.toolbar, text="Zip", command=self.zip_items, bootstyle="danger").pack(side=LEFT, padx=5)

        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=BOTH, expand=True)

        self.folder_tree = ttk.Treeview(self.main_frame, show="tree", selectmode="browse")
        self.folder_tree.pack(side=LEFT, fill=Y, padx=5, pady=5)
        self.folder_tree.bind("<<TreeviewSelect>>", self.on_folder_select)

        folder_scroll = ttk.Scrollbar(self.main_frame, orient=VERTICAL, command=self.folder_tree.yview)
        folder_scroll.pack(side=LEFT, fill=Y)
        self.folder_tree.configure(yscrollcommand=folder_scroll.set)

        self.file_table = ttk.Treeview(self.main_frame, columns=("Name", "Type", "Size", "Date"), show="headings")
        self.file_table.heading("Name", text="Name")
        self.file_table.heading("Type", text="Type")
        self.file_table.heading("Size", text="Size (Bytes)")
        self.file_table.heading("Date", text="Creation Date")
        self.file_table.column("Name", stretch=True)
        self.file_table.column("Type", width=100)
        self.file_table.column("Size", width=100)
        self.file_table.column("Date", width=150)
        self.file_table.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)
        self.file_table.bind("<Double-1>", self.open_selected_file)

        file_scroll = ttk.Scrollbar(self.main_frame, orient=VERTICAL, command=self.file_table.yview)
        file_scroll.pack(side=LEFT, fill=Y)
        self.file_table.configure(yscrollcommand=file_scroll.set)

        self.load_folder_tree()

    def load_folder_tree(self):
        self.folder_tree.delete(*self.folder_tree.get_children())
        root_node = self.folder_tree.insert("", "end", text=self.current_path, open=True)
        self.populate_tree(root_node, self.current_path)

    def populate_tree(self, parent, path):
        try:
            for item in os.listdir(path):
                full_path = os.path.join(path, item)
                if os.path.isdir(full_path):
                    node = self.folder_tree.insert(parent, "end", text=item, open=False)
                    self.folder_tree.insert(node, "end")  # Add dummy child
        except PermissionError:
            pass

    def on_folder_select(self, event):
        selected_item = self.folder_tree.selection()
        if selected_item:
            node_path = self.get_node_path(selected_item[0])
            self.current_path = node_path
            self.load_files()

    def get_node_path(self, node):
        path_parts = []
        while node:
            path_parts.insert(0, self.folder_tree.item(node, "text"))
            node = self.folder_tree.parent(node)
        return os.path.join(*path_parts)

    def load_files(self):
        for row in self.file_table.get_children():
            self.file_table.delete(row)

        try:
            for item in os.listdir(self.current_path):
                path = os.path.join(self.current_path, item)
                if os.path.isfile(path):
                    file_type = "File"
                    file_size = os.path.getsize(path)
                    file_date = time.ctime(os.path.getctime(path))
                else:
                    file_type = "Folder"
                    file_size = "-"
                    file_date = "-"
                self.file_table.insert("", "end", values=(item, file_type, file_size, file_date))
        except PermissionError:
            messagebox.showerror("Error", "Access to this folder is denied!")

    def open_folder(self):
        folder_path = filedialog.askdirectory(initialdir=self.current_path)
        if folder_path:
            self.current_path = folder_path
            self.load_folder_tree()
            self.load_files()

    def open_selected_file(self, event):
        selected_item = self.file_table.selection()
        if selected_item:
            file_name = self.file_table.item(selected_item[0], "values")[0]
            file_path = os.path.join(self.current_path, file_name)
            try:
                if os.path.isfile(file_path):
                    os.startfile(file_path)
                else:
                    self.current_path = file_path
                    self.load_folder_tree()
                    self.load_files()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {e}")

    def search_files(self):
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showinfo("Info", "Please enter a search term.")
            return

        full_path = os.path.join(self.current_path, query)
        self.file_table.delete(*self.file_table.get_children())

        if os.path.exists(full_path):
            if os.path.isfile(full_path):
                file_type = "File"
                file_size = os.path.getsize(full_path)
                file_date = time.ctime(os.path.getctime(full_path))
                self.file_table.insert("", "end", values=(os.path.basename(full_path), file_type, file_size, file_date))
            elif os.path.isdir(full_path):
                try:
                    for item in os.listdir(full_path):
                        item_path = os.path.join(full_path, item)
                        if os.path.isfile(item_path):
                            file_type = "File"
                            file_size = os.path.getsize(item_path)
                            file_date = time.ctime(os.path.getctime(item_path))
                        else:
                            file_type = "Folder"
                            file_size = "-"
                            file_date = "-"
                        self.file_table.insert("", "end", values=(item, file_type, file_size, file_date))
                except PermissionError:
                    messagebox.showerror("Error", "Access to this folder is denied!")
        else:
            results = []
            for item in os.listdir(self.current_path):
                if query.lower() in item.lower():
                    item_path = os.path.join(self.current_path, item)
                    if os.path.isfile(item_path):
                        file_type = "File"
                        file_size = os.path.getsize(item_path)
                        file_date = time.ctime(os.path.getctime(item_path))
                    else:
                        file_type = "Folder"
                        file_size = "-"
                        file_date = "-"
                    results.append((item, file_type, file_size, file_date))

            if results:
                for result in results:
                    self.file_table.insert("", "end", values=result)
            else:
                messagebox.showinfo("Info", "No matching files or folders found.")

    def create_folder(self):
        folder_name = simpledialog.askstring("Create Folder", "Enter folder name:")
        if folder_name:
            try:
                os.mkdir(os.path.join(self.current_path, folder_name))
                self.load_files()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create folder: {e}")

    def delete_item(self):
        selected_item = self.file_table.selection()
        if selected_item:
            file_name = self.file_table.item(selected_item[0], "values")[0]
            file_path = os.path.join(self.current_path, file_name)
            if messagebox.askyesno("Delete", f"Are you sure you want to delete {file_name}?"):
                try:
                    if os.path.isdir(file_path):
                        os.rmdir(file_path)
                    else:
                        os.remove(file_path)
                    self.load_files()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete file: {e}")

    def rename_item(self):
        selected_item = self.file_table.selection()
        if selected_item:
            old_name = self.file_table.item(selected_item[0], "values")[0]
            old_path = os.path.join(self.current_path, old_name)
            new_name = simpledialog.askstring("Rename", f"Enter new name for {old_name}:")
            if new_name:
                new_path = os.path.join(self.current_path, new_name)
                try:
                    os.rename(old_path, new_path)
                    self.load_files()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to rename: {e}")

    def zip_items(self):
        selected_items = self.file_table.selection()
        if not selected_items:
            messagebox.showinfo("Info", "No files selected.")
            return

        zip_name = filedialog.asksaveasfilename(defaultextension=".zip", filetypes=[("ZIP files", "*.zip")])
        if zip_name:
            try:
                with zipfile.ZipFile(zip_name, 'w') as zipf:
                    for item in selected_items:
                        file_name = self.file_table.item(item, "values")[0]
                        file_path = os.path.join(self.current_path, file_name)
                        if os.path.isfile(file_path):
                            zipf.write(file_path, arcname=file_name)
                        elif os.path.isdir(file_path):
                            for foldername, subfolders, filenames in os.walk(file_path):
                                for filename in filenames:
                                    zipf.write(os.path.join(foldername, filename), arcname=filename)
                messagebox.showinfo("Info", "Files successfully zipped.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to zip files: {e}")


if __name__ == "__main__":
    root = ttk.Window(themename="cyborg")
    app = AdvancedFileExplorer(root)
    root.mainloop()