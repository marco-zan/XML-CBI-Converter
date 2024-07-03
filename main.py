from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog

from classes.Entry import Entry
from lib.writer import export_csv
from lib.parser import parse_file

class CBIConverter(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Sample Interface")
        self.geometry("800x600")
        
        # Left frame
        left_frame = tk.Frame(self, width=240)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Title in left frame
        title_label = tk.Label(left_frame, text="Sample Title", font=("Arial", 16))
        title_label.pack(pady=10)
        
        # Import button
        import_button = tk.Button(left_frame, text="Import XML File", command=self.import_file)
        import_button.pack(pady=10)
        
        # Table with labels and values
        table_frame = tk.Frame(left_frame)
        table_frame.pack(pady=10)

        labels = ["Numero movimenti", "Totale entrate", "Totale uscite", "Totale"]
        self.values = []

        for label in labels:
            row = tk.Frame(table_frame)
            row.pack(fill=tk.X, pady=5)
            tk.Label(row, text=label, width=20, anchor="w").pack(side=tk.LEFT)
            value_label = tk.Label(row, text="0", width=10, anchor="e")
            value_label.pack(side=tk.RIGHT)
            self.values.append(value_label)
        
        # Buttons at the bottom of the left frame
        button_frame = tk.Frame(left_frame)
        button_frame.pack(pady=10)
        
        cancel_button = tk.Button(button_frame, text="Annulla", command=self.cancel)
        cancel_button.pack(side=tk.LEFT, padx=5)

        self.generate_button = tk.Button(button_frame, text="Genera CSV", command=self.generate_csv)
        self.generate_button.pack(side=tk.RIGHT, padx=5)
        self.generate_button['state'] = "disabled"
        
        # Right frame
        right_frame = tk.Frame(self)
        right_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        # Table with 5 columns
        self.tree = ttk.Treeview(right_frame, columns=("data", "data_valuta", "segno", "euro", "descrizione"), show="headings")
        
        self.tree.heading("data", text="Data")
        self.tree.heading("data_valuta", text="Data valuta")
        self.tree.heading("segno", text="Segno")
        self.tree.heading("euro", text="Euro")
        self.tree.heading("descrizione", text="Descrizione")
        
        self.tree.column("data", width=60)
        self.tree.column("data_valuta", width=60)
        self.tree.column("segno", width=8)
        self.tree.column("euro", width=55)
        self.tree.column("descrizione", width=600)
        
        self.tree.pack(expand=True, fill=tk.BOTH)

        self.sorted_entries: list[Entry] | None = None

    def import_file(self):
        file = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])

        file_path = Path(file)
        if file_path.exists():
            sorted_entries, totale_entrate, totale_uscite, totale = parse_file(file_path)

            self.values[0].config(text=str(len(sorted_entries)))
            self.values[1].config(text=f"{totale_entrate:.2f} €")
            self.values[2].config(text=f"{totale_uscite:.2f} €")
            self.values[3].config(text=f"{totale:.2f} €")

            self.tree.delete(*self.tree.get_children())
            for el in sorted_entries:
                self.tree.insert("", tk.END, values=(
                    el.data.strftime("%Y-%m-%d"),
                    el.data_valuta.strftime("%Y-%m-%d"),
                    el.sign,
                    f"{el.value:.2f} €",
                    el.description
                ))

            self.sorted_entries = sorted_entries
            self.generate_button['state'] = "normal"



    def generate_csv(self):
        file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])

        file_path = Path(file)
        if self.sorted_entries is not None:
            export_csv(file_path, self.sorted_entries)


    def cancel(self):
        print("Cancelled")

        self.generate_button['state'] = "disabled"
        # Add any additional functionality for the cancel button if needed

if __name__ == "__main__":
    app = CBIConverter()
    app.mainloop()
