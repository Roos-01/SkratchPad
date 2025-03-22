import os
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter
from pygments import lex
from pygments.lexers import PythonLexer

# Configure customtkinter appearance
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

class NotepadApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self._setup_window()
        self._initialize_state()
        self._setup_ui()
        self._bind_events()
        self._apply_initial_theme()

    def _setup_window(self):
        self.title("SkratchPad")
        self.geometry("800x600")
        self.resizable(False, False)

    def _initialize_state(self):
        self.dark_grey = "#2E2E2E"
        self.syntax_highlighting_enabled = True
        self.current_file = None
        self.lexer = PythonLexer()

    def _setup_ui(self):
        self._create_menu_frame()
        self._create_text_frame()

    def _create_menu_frame(self):
        self.menu_frame = customtkinter.CTkFrame(self, corner_radius=5)
        self.menu_frame.pack(pady=5, padx=5, fill="x")

        button_frame = customtkinter.CTkFrame(self.menu_frame, corner_radius=0, fg_color="transparent")
        button_frame.pack(expand=True)

        buttons = [
            ("New", self.new_file),
            ("Open", self.open_file),
            ("Save", self.save_file)
        ]
        for text, command in buttons:
            customtkinter.CTkButton(
                master=button_frame,
                text=text,
                command=command
            ).pack(side="left", padx=10, pady=2)

        self.highlight_switch = customtkinter.CTkSwitch(
            master=button_frame,
            text="Syntax Highlighting",
            command=self.toggle_syntax_highlighting
        )
        self.highlight_switch.pack(side="left", padx=10, pady=2)
        self.highlight_switch.select()

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

        self.scrollbar = customtkinter.CTkScrollbar(
            self.txt_frame,
            orientation="vertical",
            command=self.text_widget.yview
        )
        self.scrollbar.pack(side="right", fill="y")
        self.text_widget.config(yscrollcommand=self.scrollbar.set)

    def _bind_events(self):
        self.text_widget.bind("<KeyRelease>", self.highlight_syntax)
        self.text_widget.bind("<<Modified>>", lambda e: self.text_widget.edit_modified(False))

    def _apply_initial_theme(self):
        self._configure_syntax_tags()
        self.highlight_syntax()

    def _configure_syntax_tags(self):
        tag_configs = {
            "keyword": "#3AF8BC",
            "string": "#bb86fc",
            "comment": "#888888",
            "number": "#00ccff",
            "name": "#66ccff"
        }
        for tag, color in tag_configs.items():
            self.text_widget.tag_configure(tag, foreground=color)

    def toggle_syntax_highlighting(self):
        self.syntax_highlighting_enabled = not self.syntax_highlighting_enabled
        if not self.syntax_highlighting_enabled:
            for tag in ("keyword", "string", "comment", "number", "name"):
                self.text_widget.tag_remove(tag, "1.0", "end")
        self.highlight_syntax()

    def highlight_syntax(self, event=None):
        if not self.syntax_highlighting_enabled:
            return

        text = self.text_widget.get("1.0", "end-1c")
        for tag in ("keyword", "string", "comment", "number", "name"):
            self.text_widget.tag_remove(tag, "1.0", "end")

        pos = 0
        token_map = {
            "Keyword": "keyword",
            "String": "string",
            "Comment": "comment",
            "Number": "number",
            "Name": "name"
        }

        for token, content in lex(text + "\n", self.lexer):
            if not content.strip():
                pos += len(content)
                continue

            start = f"1.0 + {pos} chars"
            pos += len(content)
            end = f"1.0 + {pos} chars"
            token_str = str(token)

            for token_type, tag in token_map.items():
                if token_type in token_str and (token_type != "Name" or "Builtin" not in token_str):
                    self.text_widget.tag_add(tag, start, end)
                    break

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
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                self.text_widget.delete("1.0", "end")
                self.text_widget.insert("1.0", file.read())
            self.current_file = file_path
            self.title(f"SkratchPad - {os.path.basename(file_path)}")
            self.highlight_syntax()
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {str(e)}")

    def save_file(self):
        file_path = self.current_file or filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[
                ("Python Files", "*.py"),
                ("Text Files", "*.txt"),
                ("All Files", "*.*")
            ]
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(self.text_widget.get("1.0", "end-1c"))
                self.current_file = file_path
                self.title(f"SkratchPad - {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {str(e)}")

if __name__ == "__main__":
    app = NotepadApp()
    app.mainloop()
