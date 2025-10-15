# Em src/geradorEscalas/ui/widgets/ctk_calendar.py

import customtkinter as ctk
from datetime import datetime, timedelta
from calendar import monthrange
from ... import fonts

class CTkCalendar(ctk.CTkToplevel):
    def __init__(self, master, current_date=None, callback=None):
        super().__init__(master)
        self.master = master
        self.callback = callback
        self.selected_date = current_date if current_date else datetime.now().date()
        
        self.month_names_pt = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

        # --- PALETA DE CORES DO TEMA CLARO ---
        self.PRIMARY = "#0078D7"
        self.PRIMARY_HOVER = "#005EA6"
        self.SURFACE = "#FFFFFF"
        self.TEXT_PRIMARY = "#1E1E1E"
        self.TEXT_SECONDARY = "#6B6B6B"
        
        # --- CONFIGURAÇÃO DA JANELA ---
        self.configure(fg_color=self.SURFACE)
        self.title("Selecione a Data")
        self.geometry("320x340")
        self.resizable(False, False)
        
        self.transient(master); self.grab_set(); self.focus_force()
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        self.update_idletasks()
        x = master.winfo_rootx() + (master.winfo_width() // 2) - (self.winfo_width() // 2)
        y = master.winfo_rooty() + (master.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f'+{x}+{y}')

        self._create_widgets()
        self._update_calendar()

    def _create_widgets(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=10)

        self.prev_month_button = ctk.CTkButton(header_frame, text="<", width=30, command=self._prev_month, fg_color=self.PRIMARY, hover_color=self.PRIMARY_HOVER)
        self.prev_month_button.pack(side="left", padx=10)

        self.month_year_label = ctk.CTkLabel(header_frame, text="", font=fonts.SUBTITULO, text_color=self.TEXT_PRIMARY)
        self.month_year_label.pack(side="left", padx=10)

        self.next_month_button = ctk.CTkButton(header_frame, text=">", width=30, command=self._next_month, fg_color=self.PRIMARY, hover_color=self.PRIMARY_HOVER)
        self.next_month_button.pack(side="left", padx=10)

        weekdays_frame = ctk.CTkFrame(self, fg_color="transparent")
        weekdays_frame.pack(pady=5, padx=10, fill="x")
        
        weekdays = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
        for i, day in enumerate(weekdays):
            weekdays_frame.grid_columnconfigure(i, weight=1)
            ctk.CTkLabel(weekdays_frame, text=day, font=fonts.LABEL_FONT, text_color=self.TEXT_SECONDARY).grid(row=0, column=i)

        self.days_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.days_frame.pack(expand=True, fill="both", padx=10, pady=5)
        for i in range(6):
            self.days_frame.grid_rowconfigure(i, weight=1)
            for j in range(7):
                self.days_frame.grid_columnconfigure(j, weight=1)
                
    def _update_calendar(self):
        for widget in self.days_frame.winfo_children():
            widget.destroy()

        first_day_of_month = self.selected_date.replace(day=1)
        first_weekday = (first_day_of_month.weekday() + 1) % 7 
        num_days = monthrange(self.selected_date.year, self.selected_date.month)[1]
        
        month_name = self.month_names_pt[self.selected_date.month - 1]
        year = self.selected_date.year
        self.month_year_label.configure(text=f"{month_name} {year}")

        row = 0; col = first_weekday
        for day_num in range(1, num_days + 1):
            day_date = self.selected_date.replace(day=day_num)
            
            # --- LÓGICA DE ESTILO APRIMORADA ---
            fg_color = "transparent"
            text_color = self.TEXT_PRIMARY
            hover_color = "#E5E7EB" # Cinza claro para hover
            border_width = 0
            border_color = None

            # Dia atual (não selecionado)
            if day_date == datetime.now().date():
                border_width = 1
                border_color = self.PRIMARY

            # Dia selecionado
            if day_date == self.selected_date:
                fg_color = self.PRIMARY
                text_color = "white"
                hover_color = self.PRIMARY_HOVER

            day_button = ctk.CTkButton(
                self.days_frame, text=str(day_num), command=lambda d=day_date: self._select_date(d),
                width=35, height=35, fg_color=fg_color, text_color=text_color, hover_color=hover_color,
                border_width=border_width, border_color=border_color, corner_radius=8
            )
            day_button.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")

            col += 1
            if col > 6: col = 0; row += 1

    def _prev_month(self):
        self.selected_date = (self.selected_date.replace(day=1) - timedelta(days=1)).replace(day=1)
        self._update_calendar()

    def _next_month(self):
        last_day = self.selected_date.replace(day=monthrange(self.selected_date.year, self.selected_date.month)[1])
        self.selected_date = (last_day + timedelta(days=1)).replace(day=1)
        self._update_calendar()

    def _select_date(self, date_obj):
        if self.callback:
            self.callback(date_obj)
        self.destroy()

    def _on_closing(self):
        self.grab_release()
        self.destroy()