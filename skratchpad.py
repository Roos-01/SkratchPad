import os
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter
from pygments import lex
from pygments.lexers import PythonLexer

# Setup appearance and theme
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

class NotepadApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("SkratchPad")
        self.geometry("800x600")
        self.resizable(False, False)

        # Constants and state
        self.dark_grey = "#2E2E2E"
        self.syntax_highlighting_enabled = True
        self.current_file = None
        self.lexer = PythonLexer()

        # Setup UI components
        self._create_menu_frame()
        self._create_text_frame()
        self._bind_events()
        self.apply_theme()  # Configures text widget and syntax colors
        self.highlight_syntax()  # Initial syntax highlighting

    def _create_menu_frame(self):
        self.menu_frame = customtkinter.CTkFrame(self, corner_radius=5)
        self.menu_frame.pack(pady=5, padx=5, fill="x")

        self.button_frame = customtkinter.CTkFrame(self.menu_frame, corner_radius=0, fg_color="transparent")
        self.button_frame.pack(expand=True)

        self.new_button = customtkinter.CTkButton(master=self.button_frame, text="New", command=self.new_file)
        self.new_button.pack(side="left", padx=10, pady=2)

        self.open_button = customtkinter.CTkButton(master=self.button_frame, text="Open", command=self.open_file)
        self.open_button.pack(side="left", padx=10, pady=2)

        self.save_button = customtkinter.CTkButton(master=self.button_frame, text="Save", command=self.save_file)
        self.save_button.pack(side="left", padx=10, pady=2)

        self.highlight_switch = customtkinter.CTkSwitch(
            master=self.button_frame,
            text="Syntax Highlighting",
            command=self.toggle_syntax_highlighting
        )
        self.highlight_switch.pack(side="left", padx=10, pady=2)
        self.highlight_switch.select()  # Default on

    def _create_text_frame(self):
        self.txt_frame = customtkinter.CTkFrame(self, corner_radius=5)
        self.txt_frame.pack(pady=5, padx=5, fill="both", expand=True)

        self.text_widget = tk.Text(
            self.txt_frame,
            wrap="word",
            bg=self.dark_grey,
            fg="white",
            insertbackground="white",
            borderwidth=0,
            font=("Cascadia Mono", 22)
        )
        self.text_widget.pack(side="left", pady=5, padx=5, fill="both", expand=True)

        self.scrollbar = customtkinter.CTkScrollbar(self.txt_frame, orientation="vertical", command=self.text_widget.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.text_widget.config(yscrollcommand=self.scrollbar.set)

    def _bind_events(self):
        self.text_widget.bind("<KeyRelease>", self.on_key_release)
        self.text_widget.bind("<<Modified>>", self.on_text_modified)
        self.text_widget.edit_modified(False)

    def apply_theme(self):
        self.text_widget.configure(bg=self.dark_grey, fg="white")
        # Define syntax tag colors (hacker-style)
        self.text_widget.tag_configure("keyword", foreground="#3AF8BC")
        self.text_widget.tag_configure("string", foreground="#bb86fc")
        self.text_widget.tag_configure("comment", foreground="#888888")
        self.text_widget.tag_configure("number", foreground="#00ccff")
        self.text_widget.tag_configure("name", foreground="#66ccff")
        self.highlight_syntax()

    def toggle_syntax_highlighting(self):
        self.syntax_highlighting_enabled = not self.syntax_highlighting_enabled
        if self.syntax_highlighting_enabled:
            self.highlight_syntax()
        else:
            for tag in ("keyword", "string", "comment", "number", "name"):
                self.text_widget.tag_remove(tag, "1.0", "end")

    def on_key_release(self, event=None):
        self.highlight_syntax()

    def on_text_modified(self, event=None):
        if self.text_widget.edit_modified():
            self.text_widget.edit_modified(False)

    def highlight_syntax(self, event=None):
        if not self.syntax_highlighting_enabled:
            return

        text = self.text_widget.get("1.0", "end-1c")
        # Clear previous tags
        for tag in ("keyword", "string", "comment", "number", "name"):
            self.text_widget.tag_remove(tag, "1.0", "end")

        pos = 0
        for token, content in lex(text + "\n", self.lexer):
            if not content.strip():
                pos += len(content)
                continue
            start = self.text_widget.index(f"1.0 + {pos} chars")
            pos += len(content)
            end = self.text_widget.index(f"1.0 + {pos} chars")
            token_str = str(token)
            if "Keyword" in token_str:
                self.text_widget.tag_add("keyword", start, end)
            elif "String" in token_str:
                self.text_widget.tag_add("string", start, end)
            elif "Comment" in token_str:
                self.text_widget.tag_add("comment", start, end)
            elif "Number" in token_str:
                self.text_widget.tag_add("number", start, end)
            elif "Name" in token_str and "Builtin" not in token_str:
                self.text_widget.tag_add("name", start, end)

    def new_file(self):
        if messagebox.askyesno("New File", "Are you sure? Unsaved changes will be lost."):
            self.text_widget.delete("1.0", "end")
            self.current_file = None
            self.title("SkratchPad - New File")
            self.highlight_syntax()

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[
            ("Text Files", "*.txt"),
            ("Python Files", "*.py"),
            ("All Files", "*.*")
        ])
        if file_path:
            try:
                with open(file_path, "r") as file:
                    content = file.read()
                self.text_widget.delete("1.0", "end")
                self.text_widget.insert("1.0", content)
                self.current_file = file_path
                self.title(f"SkratchPad - {os.path.basename(file_path)}")
                self.highlight_syntax()
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {str(e)}")

    def save_file(self):
        if self.current_file:
            with open(self.current_file, "w", encoding="utf-8") as file:
                file.write(self.text_widget.get("1.0", "end-1c"))
        else:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".py",
                filetypes=[
                    ("Python Files", "*.py"),
                    ("Text Files", "*.txt"),
                    ("All Files", "*.*")
                ]
            )
            if file_path:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(self.text_widget.get("1.0", "end-1c"))
                self.current_file = file_path
                self.title(f"SkratchPad - {os.path.basename(file_path)}")

if __name__ == "__main__":
    app = NotepadApp()
    app.mainloop()
