from __future__ import annotations

import json
import tkinter as tk
from pathlib import Path
from queue import Queue
from tkinter import filedialog, messagebox, ttk

from ts2cad.core.config import AppConfig, ExportFormatConfig, load_config, save_config
from ts2cad.importers.generic import GenericImporter
from ts2cad.ui.worker import ConversionRequest, ConversionWorker


TEMPLATES = ["NXY", "NYX", "PNEZD", "PENZD", "NXYZ", "CUSTOM"]


class TS2CADApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("TS2CAD - Convertidora Estación Total")
        self.geometry("1200x750")

        self.config_data = load_config()
        self.files: list[Path] = []
        self.log_queue: Queue[str] = Queue()

        self._build_ui()
        self._apply_config_to_ui()

        self.after(200, self._poll_log_queue)

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        file_frame = ttk.LabelFrame(self, text="Archivos de entrada")
        file_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        file_frame.columnconfigure(1, weight=1)

        ttk.Button(file_frame, text="Seleccionar archivos", command=self._select_files).grid(row=0, column=0, padx=5, pady=5)
        self.file_list = tk.Listbox(file_frame, height=4)
        self.file_list.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        main_frame = ttk.Frame(self)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        main_frame.columnconfigure(0, weight=2)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        preview_frame = ttk.LabelFrame(main_frame, text="Vista previa (primeras 200 filas normalizadas)")
        preview_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)

        self.preview = ttk.Treeview(preview_frame, columns=("n", "x", "y", "z", "desc"), show="headings")
        for col in ("n", "x", "y", "z", "desc"):
            self.preview.heading(col, text=col)
            self.preview.column(col, width=100)
        self.preview.grid(row=0, column=0, sticky="nsew")

        rules_frame = ttk.LabelFrame(main_frame, text="Reglas y configuración")
        rules_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        rules_frame.columnconfigure(1, weight=1)

        self.decimal_comma_var = tk.BooleanVar()
        ttk.Checkbutton(rules_frame, text="Decimales con coma", variable=self.decimal_comma_var).grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=2)

        ttk.Label(rules_frame, text="Separador de entrada").grid(row=1, column=0, sticky="w", padx=5)
        self.separator_entry = ttk.Entry(rules_frame)
        self.separator_entry.grid(row=1, column=1, sticky="ew", padx=5)

        self.renumber_var = tk.BooleanVar()
        ttk.Checkbutton(rules_frame, text="Renumerar puntos", variable=self.renumber_var).grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=2)

        ttk.Label(rules_frame, text="Inicio renumeración").grid(row=3, column=0, sticky="w", padx=5)
        self.renumber_start_entry = ttk.Entry(rules_frame)
        self.renumber_start_entry.grid(row=3, column=1, sticky="ew", padx=5)

        self.layer_by_code_var = tk.BooleanVar()
        ttk.Checkbutton(rules_frame, text="Capas por código", variable=self.layer_by_code_var).grid(row=4, column=0, columnspan=2, sticky="w", padx=5, pady=2)

        ttk.Label(rules_frame, text="Diccionario códigos (JSON)").grid(row=5, column=0, sticky="w", padx=5)
        self.code_dict_path_entry = ttk.Entry(rules_frame)
        self.code_dict_path_entry.grid(row=5, column=1, sticky="ew", padx=5)

        ttk.Button(rules_frame, text="Guardar configuración", command=self._save_config).grid(row=6, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        export_frame = ttk.LabelFrame(self, text="Exportación")
        export_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        export_frame.columnconfigure(5, weight=1)

        self.export_txt_var = tk.BooleanVar(value=True)
        self.export_pnezd_var = tk.BooleanVar(value=False)
        self.export_penzd_var = tk.BooleanVar(value=False)
        self.export_csv_var = tk.BooleanVar(value=True)
        self.export_scr_var = tk.BooleanVar(value=True)
        self.export_dxf_var = tk.BooleanVar(value=True)
        self.export_report_var = tk.BooleanVar(value=True)

        ttk.Checkbutton(export_frame, text="TXT principal", variable=self.export_txt_var).grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(export_frame, text="TXT PNEZD", variable=self.export_pnezd_var).grid(row=0, column=1, sticky="w")
        ttk.Checkbutton(export_frame, text="TXT PENZD", variable=self.export_penzd_var).grid(row=0, column=2, sticky="w")
        ttk.Checkbutton(export_frame, text="CSV", variable=self.export_csv_var).grid(row=0, column=3, sticky="w")
        ttk.Checkbutton(export_frame, text="SCR", variable=self.export_scr_var).grid(row=0, column=4, sticky="w")
        ttk.Checkbutton(export_frame, text="DXF", variable=self.export_dxf_var).grid(row=0, column=5, sticky="w")
        ttk.Checkbutton(export_frame, text="Reporte", variable=self.export_report_var).grid(row=0, column=6, sticky="w")

        ttk.Label(export_frame, text="Formato TXT principal").grid(row=1, column=0, sticky="w", padx=5)
        self.template_var = tk.StringVar(value="NXY")
        template_combo = ttk.Combobox(export_frame, textvariable=self.template_var, values=TEMPLATES, state="readonly")
        template_combo.grid(row=1, column=1, sticky="w", padx=5)

        ttk.Label(export_frame, text="Patrón personalizado").grid(row=1, column=2, sticky="w", padx=5)
        self.custom_pattern_entry = ttk.Entry(export_frame, width=30)
        self.custom_pattern_entry.grid(row=1, column=3, sticky="ew", padx=5)

        ttk.Label(export_frame, text="Separador salida").grid(row=1, column=4, sticky="w", padx=5)
        self.output_separator_entry = ttk.Entry(export_frame, width=5)
        self.output_separator_entry.grid(row=1, column=5, sticky="w", padx=5)

        self.include_header_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(export_frame, text="Incluir encabezado", variable=self.include_header_var).grid(row=1, column=6, sticky="w")

        ttk.Label(export_frame, text="Decimales").grid(row=2, column=0, sticky="w", padx=5)
        self.decimals_entry = ttk.Entry(export_frame, width=5)
        self.decimals_entry.grid(row=2, column=1, sticky="w", padx=5)

        ttk.Label(export_frame, text="Carpeta destino").grid(row=2, column=2, sticky="w", padx=5)
        self.output_dir_entry = ttk.Entry(export_frame)
        self.output_dir_entry.grid(row=2, column=3, sticky="ew", padx=5)
        ttk.Button(export_frame, text="Seleccionar", command=self._select_output_dir).grid(row=2, column=4, sticky="w", padx=5)

        ttk.Label(export_frame, text="Nombre base").grid(row=2, column=5, sticky="w", padx=5)
        self.base_name_entry = ttk.Entry(export_frame, width=20)
        self.base_name_entry.grid(row=2, column=6, sticky="w", padx=5)

        ttk.Button(export_frame, text="Convertir", command=self._start_conversion).grid(row=3, column=0, columnspan=7, sticky="ew", padx=5, pady=5)

        log_frame = ttk.LabelFrame(self, text="Log")
        log_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log_text = tk.Text(log_frame, height=8)
        self.log_text.grid(row=0, column=0, sticky="nsew")

    def _select_files(self) -> None:
        file_paths = filedialog.askopenfilenames(title="Seleccionar archivos", filetypes=[("TXT/CSV", "*.txt *.csv")])
        if not file_paths:
            return
        self.files = [Path(p) for p in file_paths]
        self.file_list.delete(0, tk.END)
        for path in self.files:
            self.file_list.insert(tk.END, path.name)
        self._load_preview()

    def _load_preview(self) -> None:
        self.preview.delete(*self.preview.get_children())
        if not self.files:
            return
        importer = GenericImporter(
            decimal_comma=self.decimal_comma_var.get(),
            separator=self.separator_entry.get() or None,
        )
        result = importer.parse(self.files[0])
        for record in result.records[:200]:
            self.preview.insert("", tk.END, values=(record.n, record.x, record.y, record.z or "", record.desc))

    def _select_output_dir(self) -> None:
        directory = filedialog.askdirectory(title="Seleccionar carpeta destino")
        if directory:
            self.output_dir_entry.delete(0, tk.END)
            self.output_dir_entry.insert(0, directory)

    def _save_config(self) -> None:
        config = self._collect_config()
        save_config(config)
        messagebox.showinfo("Configuración", "Configuración guardada correctamente.")

    def _collect_config(self) -> AppConfig:
        export_format = ExportFormatConfig(
            template=self.template_var.get(),
            custom_pattern=self.custom_pattern_entry.get() or "{n} {x} {y}",
            separator=self.output_separator_entry.get() or " ",
            include_header=self.include_header_var.get(),
            decimals=int(self.decimals_entry.get() or "3"),
            decimal_comma=self.decimal_comma_var.get(),
        )
        return AppConfig(
            decimal_comma=self.decimal_comma_var.get(),
            input_separator=self.separator_entry.get() or None,
            renumber=self.renumber_var.get(),
            renumber_start=int(self.renumber_start_entry.get() or "1"),
            units_to_meters=True,
            layer_by_code=self.layer_by_code_var.get(),
            export_format=export_format,
            code_dictionary_path=self.code_dict_path_entry.get() or None,
        )

    def _apply_config_to_ui(self) -> None:
        cfg = self.config_data
        self.decimal_comma_var.set(cfg.decimal_comma)
        if cfg.input_separator:
            self.separator_entry.insert(0, cfg.input_separator)
        self.renumber_var.set(cfg.renumber)
        self.renumber_start_entry.insert(0, str(cfg.renumber_start))
        self.layer_by_code_var.set(cfg.layer_by_code)
        if cfg.code_dictionary_path:
            self.code_dict_path_entry.insert(0, cfg.code_dictionary_path)
        self.template_var.set(cfg.export_format.template)
        self.custom_pattern_entry.insert(0, cfg.export_format.custom_pattern)
        self.output_separator_entry.insert(0, cfg.export_format.separator)
        self.include_header_var.set(cfg.export_format.include_header)
        self.decimals_entry.insert(0, str(cfg.export_format.decimals))
        self.base_name_entry.insert(0, "export")

    def _start_conversion(self) -> None:
        if not self.files:
            messagebox.showwarning("Conversión", "Selecciona al menos un archivo de entrada.")
            return
        output_dir = Path(self.output_dir_entry.get() or Path.cwd())
        output_dir.mkdir(parents=True, exist_ok=True)
        base_name = self.base_name_entry.get() or "export"
        config = self._collect_config()
        layer_map = self._load_layer_map(config.code_dictionary_path)

        export_flags = {
            "txt": self.export_txt_var.get(),
            "pnezd": self.export_pnezd_var.get(),
            "penzd": self.export_penzd_var.get(),
            "csv": self.export_csv_var.get(),
            "scr": self.export_scr_var.get(),
            "dxf": self.export_dxf_var.get(),
            "report": self.export_report_var.get(),
        }

        request = ConversionRequest(
            files=self.files,
            output_dir=output_dir,
            base_name=base_name,
            config=config,
            export_flags=export_flags,
            layer_map=layer_map,
        )

        worker = ConversionWorker(request, self.log_queue, self._on_conversion_done)
        worker.start()

    def _on_conversion_done(self, report) -> None:
        self.log_queue.put(report.to_text())

    def _poll_log_queue(self) -> None:
        while not self.log_queue.empty():
            message = self.log_queue.get()
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)
        self.after(200, self._poll_log_queue)

    def _load_layer_map(self, path: str | None) -> dict[str, str]:
        if not path:
            return {}
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            self.log_queue.put("No se pudo cargar el diccionario de códigos; se usará capa por código.")
            return {}
        return {str(key): str(value) for key, value in data.items()}


def main() -> None:
    app = TS2CADApp()
    app.mainloop()


if __name__ == "__main__":
    main()
