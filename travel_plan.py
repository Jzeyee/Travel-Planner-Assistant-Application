import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
import os
import json
import datetime
import random
from PIL import Image, ImageTk
import requests
from io import BytesIO


class Enhancedtravel_plan:
    def __init__(self, root, email="user@example.com", return_home_callback=None, user_data=None):
        self.root = root
        self.email = email
        self.return_home_callback = return_home_callback
        self.user_data = user_data or {}
        self.root.title("Traney - Travel Plan")
        self.root.attributes('-fullscreen', True)
        
        # Set minimum window size
        self.root.minsize(1400, 800)
        
        # Colors matching packing.py
        self.COLORS = {
            "bg": "#f0f8ff",
            "navy": "#1e3d59",
            "dark_orange": "#ff6e40",
            "light_orange": "#ff8c66",
            "white": "#ffffff",
            "light_gray": "#f8f9fa",
            "text": "#2c3e50",
            "text_light": "#7f8c8d",
            "success": "#2ecc71",
            "danger": "#e74c3c",
            "warning": "#f39c12",
            "info": "#3498db"
        }

        self.user_data = self.load_user_data()
        self.current_page = "main"
        self.selected_city = None
        self.itinerary_data = {}
        
        # Initialize UI
        self.setup_ui()
        
    def setup_ui(self):
        """Setup main UI components"""
        # Main container
        main_container = tk.Frame(self.root, bg=self.COLORS["bg"])
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.create_header(main_container)
        self.create_main_content(main_container)
        
        self.show_main_page()
    
    def create_header(self, parent):
        """Create header matching packing.py design"""
        header_frame = tk.Frame(parent, bg=self.COLORS["navy"], height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Back button with icon
        back_btn = tk.Button(header_frame, text="◀ Home", 
                            command=self.go_home,
                            font=("Arial", 12, "bold"),
                            bg=self.COLORS["navy"],
                            fg="white",
                            activebackground=self.COLORS["dark_orange"],
                            activeforeground="white",
                            bd=0,
                            cursor="hand2",
                            padx=15)
        back_btn.pack(side="left", padx=20)
        
        # Title
        title_frame = tk.Frame(header_frame, bg=self.COLORS["navy"])
        title_frame.pack(side="left", expand=True)
        tk.Label(title_frame, text="Travel Plan Generator", 
                font=("Arial", 24, "bold"),
                fg="white", 
                bg=self.COLORS["navy"]).pack(pady=10)

    
    def create_main_content(self, parent):
        """Create main content area with scrollbar"""
        content_frame = tk.Frame(parent, bg=self.COLORS["bg"])
        content_frame.pack(fill="both", expand=True, pady=(20, 0))
        
        # Create scrollable canvas for main content
        self.canvas = tk.Canvas(content_frame, bg=self.COLORS["bg"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.main_content_frame = tk.Frame(self.canvas, bg=self.COLORS["bg"])
        self.canvas_window = self.canvas.create_window((0, 0), window=self.main_content_frame, anchor="nw")
        
        self.main_content_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        
        # This will be the main container for all content
        self.content_frame = self.main_content_frame
    
    def on_frame_configure(self, event=None):
        """Update scroll region when frame size changes"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_canvas_configure(self, event=None):
        """Update canvas window width when canvas size changes"""
        self.canvas.itemconfig(self.canvas_window, width=event.width)
    
    def load_user_data(self):
        """Load user data with error handling"""
        try:
            if os.path.exists('user_data.json'):
                with open('user_data.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'travel_plans' not in data:
                        data['travel_plans'] = []
                    return data
        except Exception as e:
            print(f"Error loading user data: {e}")
        return {'travel_plans': []}
    
    def save_user_data(self):
        """Save user data with error handling"""
        try:
            with open('user_data.json', 'w', encoding='utf-8') as f:
                json.dump(self.user_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving user data: {e}")
            return False
        
    def get_image_path(self, filename):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(BASE_DIR, "data", "images", filename)
    
    def show_main_page(self):
        """Show main travel plan page"""
        self.current_page = "main"
        
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Show main content
        self.create_modern_hero_section()
        self.create_modern_form()
        
        # Removed the content_sections frame and the call to show_modern_destinations()

    def create_modern_hero_section(self):
        """Create modern hero/banner section"""
        hero_frame = tk.Frame(self.content_frame, bg=self.COLORS['navy'])
        hero_frame.pack(fill='x', pady=(0, 30))
        
        content_frame = tk.Frame(hero_frame, bg=self.COLORS['navy'])
        content_frame.pack(fill='both', expand=True, padx=40, pady=40)
        
        tk.Label(content_frame, text="Plan Your Perfect Journey", 
                font=("Arial", 42, 'bold'), bg=self.COLORS['navy'], 
                fg="white").pack(anchor='w')
        
        tk.Label(content_frame, 
                text="AI-powered travel itineraries with personalized recommendations", 
                font=("Arial", 16), bg=self.COLORS['navy'], 
                fg="#b0c4de").pack(anchor='w', pady=(0, 30))

    def create_modern_form(self):
        """Create modern travel plan form with card design"""
        form_container = tk.Frame(self.content_frame, bg=self.COLORS['bg'])
        form_container.pack(fill='x', pady=(0, 40))
        
        form_card = tk.Frame(form_container, bg=self.COLORS['white'], 
                           relief='flat', bd=0)
        form_card.pack(fill='x', pady=10, padx=20)
        
        form_content = tk.Frame(form_card, bg=self.COLORS['white'])
        form_content.pack(fill='both', expand=True, padx=40, pady=30)

        form_header = tk.Frame(form_content, bg=self.COLORS['white'])
        form_header.pack(fill='x', pady=(0, 30))
        
        tk.Label(form_header, text="✈️", font=("Arial", 28), 
               bg=self.COLORS['white'], fg=self.COLORS['dark_orange']).pack(side='left', padx=(0, 15))
        
        header_text = tk.Frame(form_header, bg=self.COLORS['white'])
        header_text.pack(side='left')
        
        tk.Label(header_text, text="Create Travel Plan", 
                font=("Arial", 24, 'bold'), bg=self.COLORS['white'], 
                fg=self.COLORS['navy']).pack(anchor='w')
        
        tk.Label(header_text, text="Fill in your travel preferences to generate a personalized itinerary", 
                font=("Arial", 12), bg=self.COLORS['white'], 
                fg=self.COLORS['text_light']).pack(anchor='w')

        fields_frame = tk.Frame(form_content, bg=self.COLORS['white'])
        fields_frame.pack(fill='x')

        # Row 1: Destination and Duration
        row1 = tk.Frame(fields_frame, bg=self.COLORS['white'])
        row1.pack(fill='x', pady=(0, 20))
        
        self.create_form_field_card(
            row1, "📍 Destination", 
            self.create_destination_field, 
            side='left', padx=(0, 20), fill='both', expand=True
        )
        
        self.create_form_field_card(
            row1, "📅 Duration", 
            self.create_duration_field, 
            side='left', fill='both', expand=True
        )

        # Row 2: Dates and Travelers
        row2 = tk.Frame(fields_frame, bg=self.COLORS['white'])
        row2.pack(fill='x', pady=(0, 20))
        
        self.create_form_field_card(
            row2, "📅 Travel Dates", 
            self.create_dates_field, 
            side='left', padx=(0, 20), fill='both', expand=True
        )
        
        self.create_form_field_card(
            row2, "👥 Travelers", 
            self.create_travelers_field, 
            side='left', fill='both', expand=True
        )

        # Row 3: Budget and Travel Style
        row3 = tk.Frame(fields_frame, bg=self.COLORS['white'])
        row3.pack(fill='x', pady=(0, 20))
        
        self.create_form_field_card(
            row3, "💰 Budget", 
            self.create_budget_field, 
            side='left', padx=(0, 20), fill='both', expand=True
        )
        
        self.create_form_field_card(
            row3, "🎯 Travel Style",
            self.create_travel_style_field,
            fill='both', expand=True
        )

        # Row 4: Transportation Preference
        row4 = tk.Frame(fields_frame, bg=self.COLORS['white'])
        row4.pack(fill='x', pady=(0, 20))
        
        self.create_form_field_card(
            row4, "🚗 Transportation",
            self.create_transportation_field,
            fill='both', expand=True
        )

        button_frame = tk.Frame(form_content, bg=self.COLORS['white'])
        button_frame.pack(fill='x', pady=(20, 10))
        
        generate_btn = tk.Button(button_frame, text="✨ Generate Smart Plan", 
                               bg=self.COLORS['dark_orange'], fg="white",  
                               font=("Arial", 14, 'bold'), height=2,
                               command=self.generate_travel_plan, relief='flat',
                               cursor='hand2', padx=40, bd=0,
                               activebackground=self.COLORS['light_orange'])
        generate_btn.pack()
        self.add_hover_effect(generate_btn, self.COLORS['light_orange'], self.COLORS['dark_orange'])

    def create_form_field_card(self, parent, title, content_func, **pack_args):
        """Create a modern form field card"""
        card_frame = tk.Frame(parent, bg=self.COLORS['white'], relief='flat', bd=1,
                            highlightbackground="#e0e0e0",
                            highlightthickness=1)
        card_frame.pack(**pack_args)
        
        header_frame = tk.Frame(card_frame, bg=self.COLORS['white'])
        header_frame.pack(fill='x', padx=15, pady=(15, 10))
        
        tk.Label(header_frame, text=title, font=("Arial", 12, 'bold'),
                bg=self.COLORS['white'], 
                fg=self.COLORS['navy']).pack(anchor='w')
        
        content_frame = tk.Frame(card_frame, bg=self.COLORS['white'])
        content_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        content_func(content_frame)
        
        return card_frame

    def create_destination_field(self, parent):
        """Create destination field"""
        self.cities = [
            "Kuala Lumpur, Malaysia",
            "Tokyo, Japan",
            "Bangkok, Thailand",
            "Singapore, Singapore",
            "Hong Kong, China",
            "Taipei, Taiwan",
            "Shanghai, China",
            "Beijing, China",
            "Penang, Malaysia",
        ]
        
        self.destination_var = tk.StringVar()
        
        self.destination_combo = ttk.Combobox(parent, textvariable=self.destination_var,
                                            values=self.cities, font=("Arial", 11),
                                            state="readonly")
        self.destination_combo.set("Select destination")
        self.destination_combo.pack(fill='x')

    def create_duration_field(self, parent):
        """Create duration field"""
        control_frame = tk.Frame(parent, bg=self.COLORS['white'])
        control_frame.pack(fill='x')
        
        self.days_count = 3
        
        dec_btn = tk.Button(control_frame, text="−", 
                          command=self.decrease_days,
                          bg=self.COLORS['navy'], fg="white",
                          font=("Arial", 14), relief='flat', bd=0,
                          activebackground=self.COLORS['navy'],
                          cursor='hand2', width=3)
        dec_btn.pack(side='left')
        self.add_hover_effect(dec_btn, self.COLORS['navy'], self.COLORS['navy'])
        
        days_frame = tk.Frame(control_frame, bg=self.COLORS['light_gray'],
                            highlightbackground="#e0e0e0",
                            highlightthickness=1)
        days_frame.pack(side='left', padx=10, pady=5)
        
        self.days_label = tk.Label(days_frame, text=f"{self.days_count} days", 
                                 font=("Arial", 12, 'bold'), 
                                 bg=self.COLORS['light_gray'], 
                                 fg=self.COLORS['navy'],
                                 padx=20, pady=8)
        self.days_label.pack()
        
        inc_btn = tk.Button(control_frame, text="+", 
                          command=self.increase_days,
                          bg=self.COLORS['navy'], fg="white",
                          font=("Arial", 14), relief='flat', bd=0,
                          activebackground=self.COLORS['navy'],
                          cursor='hand2', width=3)
        inc_btn.pack(side='left')
        self.add_hover_effect(inc_btn, self.COLORS['navy'], self.COLORS['navy'])

    def create_dates_field(self, parent):
        """Create dates field"""
        dates_frame = tk.Frame(parent, bg=self.COLORS['white'])
        dates_frame.pack(fill='x')
        
        start_frame = tk.Frame(dates_frame, bg=self.COLORS['white'])
        start_frame.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        tk.Label(start_frame, text="Start Date", font=("Arial", 10),
                bg=self.COLORS['white'], 
                fg=self.COLORS['text_light']).pack(anchor='w', pady=(0, 5))
        
        date_input_frame = tk.Frame(start_frame, bg=self.COLORS['white'],
                                  highlightbackground="#e0e0e0",
                                  highlightthickness=1)
        date_input_frame.pack(fill='x')
        
        self.start_date_var = tk.StringVar()
        start_entry = tk.Entry(date_input_frame, width=12, font=("Arial", 11), 
                             textvariable=self.start_date_var, state='readonly',
                             relief='flat', bd=0, bg=self.COLORS['white'])
        start_entry.pack(side='left', fill='x', expand=True, padx=10, pady=8)
        
        date_btn = tk.Button(date_input_frame, text="📅", font=("Arial", 12),
                           command=lambda: self.show_calendar("start_date"), 
                           bg=self.COLORS['white'], fg=self.COLORS['navy'], 
                           relief='flat', bd=0, cursor='hand2', padx=10)
        date_btn.pack(side='right')
        
        end_frame = tk.Frame(dates_frame, bg=self.COLORS['white'])
        end_frame.pack(side='left', fill='x', expand=True)
        
        tk.Label(end_frame, text="End Date", font=("Arial", 10),
                bg=self.COLORS['white'], 
                fg=self.COLORS['text_light']).pack(anchor='w', pady=(0, 5))
        
        end_input_frame = tk.Frame(end_frame, bg=self.COLORS['white'],
                                 highlightbackground="#e0e0e0",
                                 highlightthickness=1)
        end_input_frame.pack(fill='x')
        
        self.end_date_var = tk.StringVar()
        end_entry = tk.Entry(end_input_frame, width=12, font=("Arial", 11), 
                           textvariable=self.end_date_var, state='readonly',
                           relief='flat', bd=0, bg=self.COLORS['white'])
        end_entry.pack(side='left', fill='x', expand=True, padx=10, pady=8)

    def create_travelers_field(self, parent):
        """Create travelers field"""
        control_frame = tk.Frame(parent, bg=self.COLORS['white'])
        control_frame.pack(fill='x')
        
        self.travelers_count = 2
        
        dec_btn = tk.Button(control_frame, text="−", 
                          command=self.decrease_travelers,
                          bg=self.COLORS['navy'], fg="white",
                          font=("Arial", 14), relief='flat', bd=0,
                          activebackground=self.COLORS['navy'],
                          cursor='hand2', width=3)
        dec_btn.pack(side='left')
        self.add_hover_effect(dec_btn, self.COLORS['navy'], self.COLORS['navy'])
        
        count_frame = tk.Frame(control_frame, bg=self.COLORS['light_gray'],
                             highlightbackground="#e0e0e0",
                             highlightthickness=1)
        count_frame.pack(side='left', padx=10, pady=5)
        
        count_content = tk.Frame(count_frame, bg=self.COLORS['light_gray'])
        count_content.pack(padx=20, pady=8)
        
        self.travelers_label = tk.Label(count_content, text=str(self.travelers_count), 
                                      font=("Arial", 16, 'bold'), 
                                      bg=self.COLORS['light_gray'], 
                                      fg=self.COLORS['navy'])
        self.travelers_label.pack()
        
        tk.Label(count_content, text="person(s)", font=("Arial", 10), 
                bg=self.COLORS['light_gray'], 
                fg=self.COLORS['text_light']).pack()
        
        inc_btn = tk.Button(control_frame, text="+", 
                          command=self.increase_travelers,
                          bg=self.COLORS['navy'], fg="white",
                          font=("Arial", 14), relief='flat', bd=0,
                          activebackground=self.COLORS['navy'],
                          cursor='hand2', width=3)
        inc_btn.pack(side='left')
        self.add_hover_effect(inc_btn, self.COLORS['navy'], self.COLORS['navy'])

    def create_budget_field(self, parent):
        """Create budget field"""
        self.budget_var = tk.StringVar(value="Medium (RM 1,000 - 3,000)")
        budget_options = [
            "Low (RM 500 - 1,000)", 
            "Medium (RM 1,000 - 3,000)", 
            "High (RM 3,000 - 5,000)", 
            "Luxury (RM 5,000+)"
        ]
        
        for option in budget_options:
            frame = tk.Frame(parent, bg=self.COLORS['white'])
            frame.pack(fill='x', pady=3)
            
            # Create a custom radio button
            self.create_custom_radio_button(
                frame, 
                option, 
                self.budget_var, 
                option,
                self.COLORS['navy']
            )

    def create_travel_style_field(self, parent):
        """Create travel style field with custom-styled checkboxes"""
        self.style_vars = {}
        styles = ["Adventure", "Relaxation", "Cultural", "Foodie", 
                 "Shopping", "Family", "Romantic", "Budget"]
        
        style_grid = tk.Frame(parent, bg=self.COLORS['white'])
        style_grid.pack(fill='x', pady=5)
        
        for i, style in enumerate(styles):
            var = tk.BooleanVar()
            self.style_vars[style] = var
            
            tag_frame = tk.Frame(style_grid, bg=self.COLORS['white'])
            tag_frame.pack(side='left', padx=(0, 10), pady=5)
            
            # Create custom-styled checkbox using ttk for better control
            chk = ttk.Checkbutton(
                tag_frame,
                text=style,
                variable=var,
                style="Custom.TCheckbutton"
            )
            chk.pack(side='left')
        
        # Configure ttk style for checkboxes
        self.configure_checkbox_style()

    def configure_checkbox_style(self):
        """Configure ttk checkbox style for colored checkmarks"""
        style = ttk.Style()
        
        # Create a custom style for checkboxes
        style.configure(
            "Custom.TCheckbutton",
            background=self.COLORS['white'],
            foreground=self.COLORS['navy'],
            font=("Arial", 10),
            focuscolor=self.COLORS['white'],
            padding=5
        )
        
        # Map different states
        style.map(
            "Custom.TCheckbutton",
            background=[('active', self.COLORS['light_gray']), ('selected', self.COLORS['light_gray'])],
            foreground=[('active', self.COLORS['navy']), ('selected', self.COLORS['navy'])]
        )

    def create_transportation_field(self, parent):
        """Create transportation preference field"""
        self.transportation_var = tk.StringVar(value="Public Transport")
        transport_options = [
            "Public Transport",
            "Rental Car", 
            "Taxi/Ride-share", 
            "Mix of All"
        ]
        
        for option in transport_options:
            frame = tk.Frame(parent, bg=self.COLORS['white'])
            frame.pack(fill='x', pady=3)
            
            # Create a custom radio button
            self.create_custom_radio_button(
                frame, 
                option, 
                self.transportation_var, 
                option,
                self.COLORS['navy']
            )

    def create_custom_radio_button(self, parent, text, variable, value, color):
        """Create a custom-styled radio button with proper color changes"""
        container = tk.Frame(parent, bg=self.COLORS['white'], cursor='hand2')
        container.pack(side='left')
        
        # Create canvas for the radio button indicator
        indicator = tk.Canvas(container, width=18, height=18, 
                            bg=self.COLORS['white'], 
                            highlightthickness=0)
        indicator.pack(side='left')
        
        # Draw outer circle
        outer_circle = indicator.create_oval(2, 2, 16, 16, 
                                           outline="#e0e0e0", 
                                           width=2, 
                                           fill=self.COLORS['white'])
        
        # Draw inner circle (initially hidden)
        inner_circle = indicator.create_oval(6, 6, 12, 12, 
                                           outline="", 
                                           fill="", 
                                           state='hidden')
        
        # Create label for text
        label = tk.Label(container, text=text, 
                        font=("Arial", 10),
                        bg=self.COLORS['white'], 
                        fg=self.COLORS['navy'])
        label.pack(side='left', padx=5)
        
        def update_appearance():
            """Update the appearance based on selection state"""
            if variable.get() == value:
                # Selected state
                indicator.itemconfig(outer_circle, outline=color, width=2)
                indicator.itemconfig(inner_circle, fill=color, state='normal')
                label.config(fg=color)
            else:
                # Unselected state
                indicator.itemconfig(outer_circle, outline="#e0e0e0", width=2)
                indicator.itemconfig(inner_circle, fill="", state='hidden')
                label.config(fg=self.COLORS['navy'])
        
        def select_radio():
            """Handle radio button selection"""
            variable.set(value)
            # Update all radio buttons in the same group
            self.update_radio_buttons()
        
        def on_hover(event=None):
            if variable.get() != value:
                indicator.itemconfig(outer_circle, outline=color, width=2)
                label.config(fg=color)
        
        def off_hover(event=None):
            if variable.get() != value:
                indicator.itemconfig(outer_circle, outline="#e0e0e0", width=2)
                label.config(fg=self.COLORS['navy'])
        
        # Bind events
        container.bind("<Button-1>", lambda e: select_radio())
        indicator.bind("<Button-1>", lambda e: select_radio())
        label.bind("<Button-1>", lambda e: select_radio())
        
        container.bind("<Enter>", on_hover)
        container.bind("<Leave>", off_hover)
        indicator.bind("<Enter>", on_hover)
        indicator.bind("<Leave>", off_hover)
        label.bind("<Enter>", on_hover)
        label.bind("<Leave>", off_hover)
        
        # Store references for updating
        if not hasattr(self, 'radio_buttons'):
            self.radio_buttons = []
        
        self.radio_buttons.append({
            'variable': variable,
            'value': value,
            'update_func': update_appearance,
            'container': container
        })
        
        # Initial appearance
        update_appearance()

    def update_radio_buttons(self):
        """Update all custom radio button appearances"""
        if hasattr(self, 'radio_buttons'):
            for radio in self.radio_buttons:
                radio['update_func']()

    def increase_days(self):
        if self.days_count < 30:
            self.days_count += 1
            self.days_label.config(text=f"{self.days_count} days")
            self.update_end_date()

    def decrease_days(self):
        if self.days_count > 1:
            self.days_count -= 1
            self.days_label.config(text=f"{self.days_count} days")
            self.update_end_date()

    def increase_travelers(self):
        if self.travelers_count < 20:
            self.travelers_count += 1
            self.travelers_label.config(text=str(self.travelers_count))

    def decrease_travelers(self):
        if self.travelers_count > 1:
            self.travelers_count -= 1
            self.travelers_label.config(text=str(self.travelers_count))

    def update_end_date(self):
        """Update end date based on start date and duration"""
        if self.start_date_var.get():
            try:
                start_date = datetime.datetime.strptime(self.start_date_var.get(), "%m/%d/%y")
                end_date = start_date + datetime.timedelta(days=self.days_count - 1)
                self.end_date_var.set(end_date.strftime("%m/%d/%y"))
            except:
                pass

    def show_calendar(self, date_type):
        """Show calendar for date selection"""
        cal_window = tk.Toplevel(self.root)
        cal_window.title("Select Date")
        cal_window.geometry("350x400")
        cal_window.configure(bg=self.COLORS['white'])
        cal_window.transient(self.root)
        cal_window.grab_set()
        
        x = (self.root.winfo_screenwidth() // 2) - (350 // 2)
        y = (self.root.winfo_screenheight() // 2) - (400 // 2)
        cal_window.geometry(f"+{x}+{y}")
        
        header_frame = tk.Frame(cal_window, bg=self.COLORS['navy'], height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="Select Date", 
                font=("Arial", 16, 'bold'), bg=self.COLORS['navy'], 
                fg="white").pack(pady=18)
        
        today = datetime.date.today()
        cal = Calendar(cal_window, 
                      selectmode='day',
                      year=today.year,
                      month=today.month, 
                      day=today.day,
                      mindate=today,
                      background=self.COLORS['white'],
                      foreground=self.COLORS['navy'],
                      selectbackground=self.COLORS['navy'],
                      selectforeground="white",
                      normalbackground=self.COLORS['white'])
        cal.pack(pady=20, padx=20, fill='both', expand=True)
        
        def set_date():
            selected_date = cal.get_date()
            if date_type == "start_date":
                self.start_date_var.set(selected_date)
                self.update_end_date()
            cal_window.destroy()
        
        btn_frame = tk.Frame(cal_window, bg=self.COLORS['white'])
        btn_frame.pack(pady=10)
        
        confirm_btn = tk.Button(btn_frame, text="Confirm", command=set_date,
                               bg=self.COLORS['success'], fg="white", 
                               font=("Arial", 11, 'bold'),
                               relief='flat', padx=25, pady=8, 
                               cursor='hand2', bd=0,
                               activebackground='#0da472')
        confirm_btn.pack(side='left', padx=5)
        self.add_hover_effect(confirm_btn, '#0da472', self.COLORS['success'])
        
        cancel_btn = tk.Button(btn_frame, text="Cancel", command=cal_window.destroy,
                              bg=self.COLORS['danger'], fg="white", 
                              font=("Arial", 11),
                              relief='flat', padx=25, pady=8, 
                              cursor='hand2', bd=0,
                              activebackground='#dc2626')
        cancel_btn.pack(side='left', padx=5)
        self.add_hover_effect(cancel_btn, '#dc2626', self.COLORS['danger'])

    def save_form_data(self):
        """Save current form data for later use"""
        selected_styles = [style for style, var in self.style_vars.items() if var.get()]
        
        self.itinerary_data = {
            'destination': self.destination_var.get(),
            'start_date': self.start_date_var.get(),
            'end_date': self.end_date_var.get(),
            'days': self.days_count,
            'travelers': self.travelers_count,
            'budget': self.budget_var.get(),
            'travel_styles': selected_styles,
            'transportation': self.transportation_var.get(),
            'plan_id': f"PLAN_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }

    def generate_travel_plan(self):
        """Generate travel plan based on user input"""
        if not self.destination_var.get() or self.destination_var.get() == "Select destination":
            messagebox.showwarning("Input Required", "Please select a destination city.")
            self.destination_combo.focus_set()
            return
        
        if not self.start_date_var.get():
            messagebox.showwarning("Input Required", "Please select a start date.")
            return
        
        self.save_form_data()
        
        loading_window = self.show_loading_screen()
        self.root.update()
        
        self.root.after(1500, lambda: self.finish_plan_generation(loading_window))

    def show_loading_screen(self):
        """Show loading screen while generating plan"""
        loading_window = tk.Toplevel(self.root)
        loading_window.title("Generating Plan")
        loading_window.geometry("400x200")
        loading_window.configure(bg=self.COLORS['white'])
        loading_window.transient(self.root)
        loading_window.grab_set()
        
        x = (self.root.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (200 // 2)
        loading_window.geometry(f"+{x}+{y}")
        
        tk.Label(loading_window, text="🎯", font=("Arial", 40), 
                bg=self.COLORS['white'], fg=self.COLORS['dark_orange']).pack(pady=(20, 10))
        
        tk.Label(loading_window, text="Creating Your Perfect Itinerary", 
                font=("Arial", 16, 'bold'), bg=self.COLORS['white'], 
                fg=self.COLORS['navy']).pack()
        
        tk.Label(loading_window, text="Analyzing preferences and generating recommendations...", 
                font=("Arial", 11), bg=self.COLORS['white'], 
                fg=self.COLORS['text_light']).pack(pady=(5, 20))
        
        progress_frame = tk.Frame(loading_window, bg=self.COLORS['white'])
        progress_frame.pack(pady=10)
        
        progress_bar = ttk.Progressbar(progress_frame, maximum=100, 
                                      length=300, mode='indeterminate')
        progress_bar.pack()
        progress_bar.start(10)
        
        return loading_window

    def finish_plan_generation(self, loading_window):
        """Finish plan generation and show results"""
        loading_window.destroy()
        self.show_travel_details()

    def show_travel_details(self):
        """Open travel details window with the itinerary data"""
        from travel_detail import TravelDetail
        # Create new window for travel details
        detail_window = tk.Toplevel(self.root)
        detail_window.title("Travel Plan Details")
        detail_window.geometry("1400x900")
        detail_window.minsize(1400, 800)
        
        # Pass the itinerary data and user data to the detail window
        detail_app = TravelDetail(detail_window, self.itinerary_data, self.user_data, self.email)
        
        # Make the detail window modal
        detail_window.transient(self.root)
        detail_window.grab_set()
        detail_window.focus_set()
        
        # Center the window
        detail_window.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (900 // 2)
        detail_window.geometry(f"+{x}+{y}")

    def add_hover_effect(self, widget, hover_color, normal_color):
        widget.bind("<Enter>", lambda e: widget.config(bg=hover_color) if widget.cget("state") != "disabled" else None)
        widget.bind("<Leave>", lambda e: widget.config(bg=normal_color) if widget.cget("state") != "disabled" else None)

    def on_mousewheel(self, event):
        if event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        else:
            self.canvas.yview_scroll(1, "units")

    # ==================== PROFILE METHODS ====================
    
    def show_profile_menu(self):
        """Show profile dropdown menu"""
        menu = tk.Menu(self.root, tearoff=0, bg="white", font=("Arial", 10))
        
        menu.add_command(label=f"User: {self.email}", state="disabled")
        menu.add_separator()
        menu.add_command(label="⚙️ Settings", command=self.open_settings)
        menu.add_command(label="📋 My Plans", command=self.open_my_plans)
        menu.add_separator()
        menu.add_command(label="🚪 Logout", command=self.logout)
        
        x = self.root.winfo_pointerx()
        y = self.root.winfo_pointery() + 20
        menu.tk_popup(x, y)
    
    def open_settings(self):
        messagebox.showinfo("Account Settings", "Account settings will be available soon!")
    
    def open_my_plans(self):
        if self.user_data.get('travel_plans'):
            plans_text = "\n".join([f"• {plan.get('destination', 'Unknown')} ({plan.get('start_date', 'N/A')})" 
                                   for plan in self.user_data['travel_plans'][-5:]])
            messagebox.showinfo("My Travel Plans", f"Your recent travel plans:\n\n{plans_text}")
        else:
            messagebox.showinfo("My Travel Plans", "You haven't created any travel plans yet!")
    
    def go_home(self):
        """Return to home page"""
        self.root.destroy()
        
        if self.return_home_callback:
            self.return_home_callback()
        else:
            # Try to launch home.py
            try:
                import home
                root = tk.Tk()
                try:
                    app = home.HomeApp(root, self.email)
                except TypeError:
                    try:
                        user_name = self.user_data.get('name', 'User')
                        app = home.HomeApp(root, self.email, user_name)
                    except TypeError:
                        app = home.HomeApp(root)
                root.mainloop()
            except ImportError:
                import subprocess
                import sys
                try:
                    subprocess.Popen([sys.executable, "home.py"])
                except:
                    home_window = tk.Tk()
                    home_window.title("TravelEase - Home")
                    home_window.geometry("800x600")
                    home_window.configure(bg=self.COLORS["bg"])
                    
                    header = tk.Frame(home_window, bg=self.COLORS["navy"], height=100)
                    header.pack(fill="x")
                    header.pack_propagate(False)
                    
                    tk.Label(header, text="🏠 TravelEase Home", 
                            font=("Arial", 28, "bold"),
                            fg="white", 
                            bg=self.COLORS["navy"]).pack(pady=30)
                    
                    content = tk.Frame(home_window, bg=self.COLORS["bg"])
                    content.pack(fill="both", expand=True, padx=40, pady=40)
                    
                    tk.Label(content, text="Welcome to TravelEase!", 
                            font=("Arial", 24, "bold"),
                            bg=self.COLORS["bg"],
                            fg=self.COLORS["navy"]).pack(pady=20)
                    
                    tk.Label(content, text="Your one-stop travel planning solution", 
                            font=("Arial", 16),
                            bg=self.COLORS["bg"],
                            fg=self.COLORS["text_light"]).pack(pady=10)
                    
                    features = [
                        "✈️ Travel Plan - Create personalized itineraries",
                        "🧳 Packing List - Plan what to pack",
                        "🏨 Accommodation - Find and book hotels",
                        "🏛️ Attractions - Discover local attractions",
                        "🚗 Transportation - Book rides and tickets"
                    ]
                    
                    for feature in features:
                        tk.Label(content, text=feature, 
                                font=("Arial", 14),
                                bg=self.COLORS["bg"],
                                fg=self.COLORS["text"]).pack(anchor="w", pady=8)
                    
                    travel_btn = tk.Button(content,
                                          text="✈️ Create Travel Plan",
                                          command=lambda: self.open_travel_plan(home_window),
                                          font=("Arial", 14, "bold"),
                                          bg=self.COLORS["dark_orange"],
                                          fg="white",
                                          bd=0,
                                          cursor="hand2",
                                          padx=30,
                                          pady=15)
                    travel_btn.pack(pady=40)
                    
                    home_window.mainloop()
    
    def open_travel_plan(self, home_window):
        """Open travel plan from home window"""
        home_window.destroy()
        root = tk.Tk()
        app = Enhancedtravel_plan(root, email=self.email, user_data=self.user_data)
        root.mainloop()
    
    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
            try:
                import main
                root = tk.Tk()
                app = main.LoginApp(root)
                root.mainloop()
            except ImportError:
                print("Login module not found")


# Main execution
if __name__ == "__main__":
    root = tk.Tk()
    app = Enhancedtravel_plan(root)
    root.mainloop()