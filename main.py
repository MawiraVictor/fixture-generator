import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.font import Font
import pandas as pd
from fixtures import FixtureGenerator, FixtureValidator, FixtureExporter

class FixtureGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("   ABC Premier League Fixture Generator  ")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        self.setup_styles()
        self.setup_ui()
        
        # Initialize backend components
        try:
            self.generator = FixtureGenerator('data/teams.csv')
            self.validator = FixtureValidator()
            self.exporter = FixtureExporter()
            self.status_var.set("Ready to generate fixtures")
        except Exception as e:
            self.show_error(f"Initialization failed: {str(e)}")
            self.status_var.set("Failed to initialize - check team data")

    def setup_styles(self):
        """Configure modern UI styles"""
        self.style = ttk.Style()
        
        # Fonts
        self.title_font = Font(family="Helvetica", size=16, weight="bold")
        self.button_font = Font(family="Helvetica", size=10)
        self.tree_font = Font(family="Consolas", size=10)
        
        # Colors
        self.style.configure('TFrame', background="#f1e6e6")# Light background for frames
        self.style.configure('TLabel', background="#f0f0f0ff", font=('Helvetica', 10))
        self.style.configure('TButton', font=self.button_font, padding=6)
        self.style.map('TButton',
            foreground=[('active', 'white'), ('!active', 'black')],
            background=[('active', '#4a6baf'), ('!active', '#f0f0f0')]
        )

    def setup_ui(self):
        """Build the interface"""
        # Header Frame
        header_frame = ttk.Frame(self.root, padding=(20, 10, 20, 0))
        header_frame.pack(fill=tk.X)
        
        ttk.Label(
            header_frame,
            text="⚽ ABC Premier League Fixture Generator",
            font=self.title_font,
            foreground="#1f6cb9"
        ).pack(pady=(0, 10))

        # Control Panel
        control_frame = ttk.Frame(self.root, padding=(20, 5, 20, 5))
        control_frame.pack(fill=tk.X)
        
        self.generate_btn = ttk.Button(
            control_frame,
            text="▶ Generate Fixtures",
            command=self.generate_fixtures,
            style='TButton'
        )
        self.generate_btn.pack(side=tk.LEFT, padx=5)
        
        # Export buttons frame
        export_frame = ttk.Frame(control_frame)
        export_frame.pack(side=tk.LEFT, padx=10)
        
        self.csv_btn = ttk.Button(
            export_frame,
            text="📊 CSV",
            command=lambda: self.export_fixtures('csv'),
            state=tk.DISABLED
        )
        self.csv_btn.pack(side=tk.LEFT, padx=2)
        
        self.json_btn = ttk.Button(
            export_frame,
            text="📝 JSON",
            command=lambda: self.export_fixtures('json'),
            state=tk.DISABLED
        )
        self.json_btn.pack(side=tk.LEFT, padx=2)
        
        self.excel_btn = ttk.Button(
            export_frame,
            text="📈 Excel",
            command=lambda: self.export_fixtures('xlsx'),
            state=tk.DISABLED
        )
        self.excel_btn.pack(side=tk.LEFT, padx=2)

        # Fixtures Table Frame
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
        
        # Treeview with scrollbars
        self.tree = ttk.Treeview(
            table_frame,
            columns=('Home', 'Away', 'Weekend', 'Leg', 'Stadium', 'Town'),
            show='headings',
            selectmode='browse',
            style='Treeview'
        )
        
        # Configure columns
        columns = {
            'Home': {'text': 'Home Team', 'width': 150},
            'Away': {'text': 'Away Team', 'width': 150},
            'Weekend': {'text': 'Weekend', 'width': 80},
            'Leg': {'text': 'Leg', 'width': 50},
            'Stadium': {'text': 'Stadium', 'width': 180},
            'Town': {'text': 'Town', 'width': 120}
        }
        
        for col, config in columns.items():
            self.tree.heading(col, text=config['text'], anchor=tk.W)
            self.tree.column(col, width=config['width'], stretch=tk.NO)

        # Scrollbars
        y_scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        x_scroll = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky=tk.NSEW)
        y_scroll.grid(row=0, column=1, sticky=tk.NS)
        x_scroll.grid(row=1, column=0, sticky=tk.EW)
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Status Bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to generate fixtures")
        
        status_bar = ttk.Frame(self.root, relief=tk.SUNKEN, padding=(10, 5, 10, 5))
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        ttk.Label(
            status_bar,
            textvariable=self.status_var,
            anchor=tk.W
        ).pack(fill=tk.X)

    def generate_fixtures(self):
        """Generate and display fixtures with proper field mapping"""
        try:
            self.status_var.set("Generating fixtures...")
            self.root.config(cursor="watch")
            self.root.update()
            
            # Disable buttons during operation
            self.generate_btn.config(state=tk.DISABLED)
            self.csv_btn.config(state=tk.DISABLED)
            self.json_btn.config(state=tk.DISABLED)
            self.excel_btn.config(state=tk.DISABLED)
            
            # Generate fixtures
            fixtures = self.generator.generate_fixtures()
            
            # Validate fixture structure
            if not isinstance(fixtures, dict) or 'matches' not in fixtures:
                raise ValueError("Invalid fixture structure: Missing 'matches' key")
                
            # Clear existing data
            self.tree.delete(*self.tree.get_children())
                
            # Populate table with correct field mapping
            for match in fixtures['matches']:
                try:
                    self.tree.insert('', tk.END, values=(
                        match['Home Team'],
                        match['Away Team'],
                        match['Weekend'],
                        match['Leg'],
                        match['Stadium'],
                        match['Town']
                    ))
                    
                except KeyError as e:
                    self.show_warning("Invalid Match Data", f"Skipping invalid match: Missing {str(e)}")
                    continue
            
            # Validate fixtures
            errors = self.validator.validate(fixtures, self.generator.teams)
            if errors:
                self.show_warning("Validation Issues", "\n".join(f"• {error}" for error in errors))
                self.status_var.set("Validation completed with warnings")
            else:
                self.status_var.set("Fixtures generated successfully!")
                self.csv_btn.config(state=tk.NORMAL)
                self.json_btn.config(state=tk.NORMAL)
                self.excel_btn.config(state=tk.NORMAL)
                
        except Exception as e:
            self.show_error(f"Generation failed: {str(e)}")
            self.status_var.set("Error occurred during generation")
        finally:
            self.root.config(cursor="")
            self.generate_btn.config(state=tk.NORMAL)

    def export_fixtures(self, format_type):
        """Export fixtures to selected location in specific format"""
        try:
            self.root.config(cursor="watch")
            self.root.update()
            
            fixtures = self.generator.generate_fixtures()
            export_path = filedialog.asksaveasfilename(
                title=f"Save As {format_type.upper()}",
                defaultextension=f".{format_type}",
                filetypes=[(f"{format_type.upper()} files", f"*.{format_type}")]
            )
            
            if export_path:
                self.status_var.set(f"Exporting {format_type.upper()}...")
                self.root.update()
                
                # Create DataFrame from fixtures
                df = pd.DataFrame(fixtures['matches'])
                
                # Export based on format type
                if format_type == 'csv':
                    df.to_csv(export_path, index=False)
                elif format_type == 'json':
                    df.to_json(export_path, orient='records', indent=2)
                elif format_type == 'xlsx':
                    df.to_excel(export_path, index=False)
                
                self.show_info(
                    "Export Successful",
                    f"Fixtures exported to:\n{export_path}"
                )
                self.status_var.set(f"{format_type.upper()} exported successfully")
                
        except Exception as e:
            self.show_error(f"Export failed: {str(e)}")
            self.status_var.set(f"{format_type.upper()} export failed")
        finally:
            self.root.config(cursor="")

    def show_error(self, message):
        """Show error message dialog"""
        messagebox.showerror(
            "Error",
            message,
            parent=self.root
        )

    def show_warning(self, title, message):
        """Show warning message dialog"""
        messagebox.showwarning(
            title,
            message,
            parent=self.root
        )

    def show_info(self, title, message):
        """Show info message dialog"""
        messagebox.showinfo(
            title,
            message,
            parent=self.root
        )

if __name__ == "__main__":
    root = tk.Tk()
    try:
        app = FixtureGeneratorApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"Application failed to start:\n{str(e)}")