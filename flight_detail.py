import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import random

class FlightDetailPage:
    """Flight details and seat selection page"""
    def __init__(self, root, flight_data, adult_count, child_count, 
                 departure_var, return_var, flight_type_var, class_var,
                 going_var, colors, email, profile_system, 
                 return_to_main_callback, open_booking_detail_callback):
        """
        Initialize the flight details page
        """
        self.root = root
        self.flight_data = flight_data
        self.adult_count = adult_count
        self.child_count = child_count
        self.departure_var = departure_var
        self.return_var = return_var
        self.flight_type_var = flight_type_var
        self.class_var = class_var
        self.going_var = going_var
        self.colors = colors
        self.email = email
        self.profile_system = profile_system
        self.return_to_main_callback = return_to_main_callback
        self.open_booking_detail_callback = open_booking_detail_callback
        self.root.attributes('-fullscreen', True)
        
        self.selected_seats = []
        self.seat_buttons = {}
        
        self.setup_page()

    def setup_page(self):
        """Set up the flight details page"""
        # Create main container
        self.main_container = tk.Frame(self.root, bg='#f5f7fa')
        self.main_container.pack(fill='both', expand=True, padx=25, pady=15)
        
        # Create scrollable canvas
        canvas_frame = tk.Frame(self.main_container, bg='#f5f7fa')
        canvas_frame.pack(fill='both', expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, bg='#f5f7fa', highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='#f5f7fa')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create page content
        self.create_header_section()
        self.create_two_column_layout()  # Create two-column layout
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel scrolling
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", self._on_mousewheel)

    def create_header_section(self):
        """Create header with back button and title"""
        header_frame = tk.Frame(self.scrollable_frame, bg='#f5f7fa')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Back button
        back_btn = tk.Button(header_frame, text="← Back to Flights", 
                           font=('Arial', 11, 'bold'), bg="#1e3d59", fg='white',
                           command=self.return_to_main_callback, relief='flat', cursor='hand2',
                           padx=18, pady=8, bd=0)
        back_btn.pack(side='left')
        back_btn.bind("<Enter>", lambda e: back_btn.config(bg="#2c4e50"))
        back_btn.bind("<Leave>", lambda e: back_btn.config(bg="#1e3d59"))
        
        # Title
        title_label = tk.Label(header_frame, text="Flight Details", 
                              font=('Arial', 18, 'bold'), bg='#f5f7fa', fg='#1e3d59')
        title_label.pack(side='right')

    def create_two_column_layout(self):
        """Create two-column layout: Left for content, Right for price/details"""
        self.main_content_frame = tk.Frame(self.scrollable_frame, bg='#f5f7fa')
        self.main_content_frame.pack(fill='both', expand=True)
        
        # Left column (70% width) - Content
        self.left_column = tk.Frame(self.main_content_frame, bg='#f5f7fa')
        self.left_column.pack(side='left', fill='both', expand=True, padx=(0, 15))
        
        # Right column (30% width) - Price & Summary
        self.right_column = tk.Frame(self.main_content_frame, bg='#f5f7fa', width=350)
        self.right_column.pack(side='right', fill='y', padx=(15, 0))
        self.right_column.pack_propagate(False)  # Keep fixed width
        
        # Create content in left column
        self.create_flight_summary_card_left()
        self.create_flight_details_card_left()
        self.create_passenger_selection_card()
        self.create_seat_selection_card()
        
        # Create price summary in right column
        self.create_price_summary_card()
        
        # Create action buttons at bottom
        self.create_action_buttons()

    def create_flight_summary_card_left(self):
        """Create flight summary card in left column"""
        card = tk.Frame(self.left_column, bg='white', relief='groove', bd=1)
        card.pack(fill='x', pady=(0, 20))
        
        # Header
        header = tk.Frame(card, bg='#1e3d59')
        header.pack(fill='x')
        tk.Label(header, text="✈️ Flight Summary", 
                font=('Arial', 14, 'bold'), bg='#1e3d59', fg='white', 
                padx=20, pady=12).pack(side='left')
        
        # Content
        content = tk.Frame(card, bg='white')
        content.pack(fill='x', padx=25, pady=25)
        
        # Airline and route
        tk.Label(content, text=self.flight_data['airline'], 
                font=('Arial', 16, 'bold'), bg='white', fg='#1e3d59').pack(anchor='w')
        
        # Get route information
        route_text = self.flight_data.get('route', '')
        if not route_text and self.going_var.get() != "Select destination":
            route_text = f"Kuala Lumpur → {self.going_var.get().split(',')[0]}"
        
        tk.Label(content, text=route_text, 
                font=('Arial', 14), bg='white', fg='#666666').pack(anchor='w', pady=(2, 0))
        
        # Flight details
        flight_num = self.flight_data.get('flight_number', f"FL{random.randint(100, 999)}")
        tk.Label(content, text=f"Flight: {flight_num} | Aircraft: {self.flight_data['aircraft']}", 
                font=('Arial', 11), bg='white', fg='#333333').pack(anchor='w', pady=(10, 0))
        
        # Departure date
        tk.Label(content, text=f"Departure: {self.departure_var.get()}", 
                font=('Arial', 11), bg='white', fg='#333333').pack(anchor='w', pady=(5, 0))

    def create_flight_details_card_left(self):
        """Create flight details card in left column"""
        card = tk.Frame(self.left_column, bg='white', relief='groove', bd=1)
        card.pack(fill='x', pady=(0, 20))
        
        header = tk.Frame(card, bg='#1e3d59')
        header.pack(fill='x')
        tk.Label(header, text="📅 Flight Schedule", 
                font=('Arial', 14, 'bold'), bg='#1e3d59', fg='white', 
                padx=20, pady=12).pack(side='left')
        
        content = tk.Frame(card, bg='white')
        content.pack(fill='x', padx=25, pady=25)
        
        # Departure and arrival times with safe handling
        time_str = self.flight_data.get('time', '08:00 - 16:00')
        time_parts = time_str.split(' - ')
        departure_time = time_parts[0] if len(time_parts) > 0 else "08:00"
        arrival_time = time_parts[1] if len(time_parts) > 1 else "16:00"
        
        # Timeline layout
        timeline_frame = tk.Frame(content, bg='white')
        timeline_frame.pack(fill='x', pady=(0, 20))
        
        # Departure
        departure_col = tk.Frame(timeline_frame, bg='white')
        departure_col.pack(side='left', padx=(0, 50))
        tk.Label(departure_col, text="Departure", font=('Arial', 12, 'bold'), 
                bg='white', fg='#1e3d59').pack(anchor='w')
        tk.Label(departure_col, text=departure_time, font=('Arial', 18, 'bold'), 
                bg='white', fg='#333333').pack(anchor='w', pady=(5, 0))
        tk.Label(departure_col, text="Kuala Lumpur", font=('Arial', 11), 
                bg='white', fg='#666666').pack(anchor='w')
        
        # Flight duration
        middle_col = tk.Frame(timeline_frame, bg='white')
        middle_col.pack(side='left', padx=(50, 50))
        tk.Label(middle_col, text="⏱️", font=('Arial', 24), 
                bg='white', fg='#1e3d59').pack()
        tk.Label(middle_col, text=self.flight_data['duration'], font=('Arial', 14, 'bold'), 
                bg='white', fg='#333333').pack(pady=(5, 0))
        tk.Label(middle_col, text="Flight Time", font=('Arial', 11), 
                bg='white', fg='#666666').pack()
        
        # Arrival
        arrival_col = tk.Frame(timeline_frame, bg='white')
        arrival_col.pack(side='left', padx=(50, 0))
        tk.Label(arrival_col, text="Arrival", font=('Arial', 12, 'bold'), 
                bg='white', fg='#1e3d59').pack(anchor='w')
        tk.Label(arrival_col, text=arrival_time, font=('Arial', 18, 'bold'), 
                bg='white', fg='#333333').pack(anchor='w', pady=(5, 0))
        
        # Additional details
        details_frame = tk.Frame(content, bg='white')
        details_frame.pack(fill='x')
        
        # Stops information
        stops_frame = tk.Frame(details_frame, bg='white')
        stops_frame.pack(side='left', padx=(0, 30))
        tk.Label(stops_frame, text="Stops", font=('Arial', 11, 'bold'), 
                bg='white', fg='#1e3d59').pack(anchor='w')
        stops_text = self.flight_data['stops']
        stops_color = '#27ae60' if "Non-stop" in stops_text else '#e74c3c'
        tk.Label(stops_frame, text=stops_text, font=('Arial', 12), 
                bg='white', fg=stops_color).pack(anchor='w', pady=(2, 0))
        
        # Class information
        class_frame = tk.Frame(details_frame, bg='white')
        class_frame.pack(side='left', padx=(30, 0))
        tk.Label(class_frame, text="Class", font=('Arial', 11, 'bold'), 
                bg='white', fg='#1e3d59').pack(anchor='w')
        tk.Label(class_frame, text=self.class_var.get(), font=('Arial', 12), 
                bg='white', fg='#333333').pack(anchor='w', pady=(2, 0))

    def create_passenger_selection_card(self):
        """Create passenger selection card"""
        self.passenger_card = tk.Frame(self.left_column, bg='white', relief='groove', bd=1)
        self.passenger_card.pack(fill='x', pady=(0, 20))
        
        # Header
        header = tk.Frame(self.passenger_card, bg='#1e3d59')
        header.pack(fill='x')
        tk.Label(header, text="👥 Select Passengers", 
                font=('Arial', 14, 'bold'), bg='#1e3d59', fg='white', 
                padx=20, pady=12).pack(side='left')
        
        # Content
        self.passenger_content = tk.Frame(self.passenger_card, bg='white')
        self.passenger_content.pack(fill='x', padx=25, pady=25)
        
        # Instructions
        tk.Label(self.passenger_content, text="Step 1: Choose number of passengers before selecting seats", 
                font=('Arial', 12, 'bold'), bg='white', fg='#1e3d59').pack(anchor='w', pady=(0, 20))
        
        # Adult count
        adult_frame = tk.Frame(self.passenger_content, bg='white')
        adult_frame.pack(fill='x', pady=(0, 15))
        tk.Label(adult_frame, text="Adults (12+ years):", 
                font=('Arial', 11), bg='white', fg='#333333').pack(side='left')
        
        self.adult_var = tk.IntVar(value=self.adult_count)
        self.adult_spinbox = tk.Spinbox(adult_frame, from_=1, to=10, 
                                       textvariable=self.adult_var,
                                       font=('Arial', 11), width=5,
                                       command=self.update_passenger_counts)
        self.adult_spinbox.pack(side='right')
        
        # Child count
        child_frame = tk.Frame(self.passenger_content, bg='white')
        child_frame.pack(fill='x', pady=(0, 25))
        tk.Label(child_frame, text="Children (2-11 years):", 
                font=('Arial', 11), bg='white', fg='#333333').pack(side='left')
        
        self.child_var = tk.IntVar(value=self.child_count)
        self.child_spinbox = tk.Spinbox(child_frame, from_=0, to=10, 
                                       textvariable=self.child_var,
                                       font=('Arial', 11), width=5,
                                       command=self.update_passenger_counts)
        self.child_spinbox.pack(side='right')
        
        # Total summary
        self.total_frame = tk.Frame(self.passenger_content, bg='#f8f9fa', relief='solid', bd=1, padx=15, pady=10)
        self.total_frame.pack(fill='x', pady=(10, 0))
        
        self.total_label = tk.Label(self.total_frame, 
                text=f"Total Passengers: {self.adult_count + self.child_count}",
                font=('Arial', 12, 'bold'), bg='#f8f9fa', fg='#1e3d59')
        self.total_label.pack()

    def create_seat_selection_card(self):
        """Create seat selection card"""
        self.seat_card = tk.Frame(self.left_column, bg='white', relief='groove', bd=1)
        self.seat_card.pack(fill='x', pady=(0, 20))
        
        # Header
        header = tk.Frame(self.seat_card, bg='#1e3d59')
        header.pack(fill='x')
        tk.Label(header, text="💺 Select Seats", 
                font=('Arial', 14, 'bold'), bg='#1e3d59', fg='white', 
                padx=20, pady=12).pack(side='left')
        
        # Content
        self.seat_content = tk.Frame(self.seat_card, bg='white')
        self.seat_content.pack(fill='x', padx=25, pady=25)
        
        # Instructions
        instructions_frame = tk.Frame(self.seat_content, bg='white')
        instructions_frame.pack(fill='x', pady=(0, 15))
        
        self.instructions_label = tk.Label(instructions_frame, 
                text="Step 2: Click on available seats (green) to select",
                font=('Arial', 11), bg='white', fg='#666666')
        self.instructions_label.pack(anchor='w')
        
        # Seat selection status
        status_frame = tk.Frame(self.seat_content, bg='white')
        status_frame.pack(fill='x', pady=(0, 20))
        
        self.seat_status_label = tk.Label(status_frame, 
                text=f"Selected {len(self.selected_seats)} of {self.adult_count + self.child_count} required seats",
                font=('Arial', 11), bg='white', fg='#666666')
        self.seat_status_label.pack(side='left')
        
        # Create seat map
        self.create_seat_map()

    def create_seat_map(self):
        """Create the interactive seat map"""
        seat_layout = [
            ["1A", "1B", "1C", "  ", "1D", "1E", "1F"],
            ["2A", "2B", "2C", "  ", "2D", "2E", "2F"],
            ["3A", "3B", "3C", "  ", "3D", "3E", "3F"],
            ["4A", "4B", "4C", "  ", "4D", "4E", "4F"],
            ["5A", "5B", "5C", "  ", "5D", "5E", "5F"],
            ["6A", "6B", "6C", "  ", "6D", "6E", "6F"],
            ["7A", "7B", "7C", "  ", "7D", "7E", "7F"],
            ["8A", "8B", "8C", "  ", "8D", "8E", "8F"],
            ["9A", "9B", "9C", "  ", "9D", "9E", "9F"],
            ["10A", "10B", "10C", "  ", "10D", "10E", "10F"]
        ]
        
        seat_status = {
            "1A": "available", "1B": "available", "1C": "available", "1D": "available", "1E": "available", "1F": "available",
            "2A": "occupied", "2B": "occupied", "2C": "available", "2D": "available", "2E": "occupied", "2F": "available",
            "3A": "available", "3B": "available", "3C": "available", "3D": "available", "3E": "available", "3F": "available",
            "4A": "premium", "4B": "premium", "4C": "premium", "4D": "premium", "4E": "premium", "4F": "premium",
            "5A": "available", "5B": "available", "5C": "available", "5D": "available", "5E": "available", "5F": "available",
            "6A": "exit", "6B": "exit", "6C": "exit", "6D": "exit", "6E": "exit", "6F": "exit",
            "7A": "available", "7B": "available", "7C": "available", "7D": "available", "7E": "available", "7F": "available",
            "8A": "occupied", "8B": "available", "8C": "available", "8D": "available", "8E": "available", "8F": "occupied",
            "9A": "available", "9B": "available", "9C": "available", "9D": "available", "9E": "available", "9F": "available",
            "10A": "available", "10B": "available", "10C": "available", "10D": "available", "10E": "available", "10F": "available"
        }
        
        seat_colors = {
            "available": "#4CAF50",
            "selected": "#2196F3", 
            "occupied": "#f44336",
            "premium": "#FF9800",
            "exit": "#9C27B0"
        }
        
        # Legend
        legend_frame = tk.Frame(self.seat_content, bg='#f8f9fa', relief='solid', bd=1, padx=15, pady=10)
        legend_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(legend_frame, text="Seat Status Legend", 
                font=('Arial', 12, 'bold'), bg='#f8f9fa', fg='#1e3d59').pack(anchor='w', pady=(0, 8))
        
        legend_items = tk.Frame(legend_frame, bg='#f8f9fa')
        legend_items.pack(fill='x')
        
        legend_data = [
            ("Available", "#4CAF50"),
            ("Selected", "#2196F3"),
            ("Occupied", "#f44336"),
            ("Premium", "#FF9800"),
            ("Exit Row", "#9C27B0")
        ]
        
        for i, (text, color) in enumerate(legend_data):
            item_frame = tk.Frame(legend_items, bg='#f8f9fa')
            item_frame.pack(side='left', padx=(0, 15))
            tk.Frame(item_frame, bg=color, width=15, height=15).pack(side='left', padx=(0, 5))
            tk.Label(item_frame, text=text, font=('Arial', 9), 
                    bg='#f8f9fa', fg='#333333').pack(side='left')
        
        # Cockpit label
        cockpit_frame = tk.Frame(self.seat_content, bg='white')
        cockpit_frame.pack(pady=(0, 10))
        tk.Label(cockpit_frame, text="✈️ COCKPIT", font=('Arial', 12, 'bold'), 
                bg='white', fg='#1e3d59').pack()
        
        # Create seat buttons
        self.seat_buttons = {}
        
        for row_idx, row in enumerate(seat_layout):
            row_frame = tk.Frame(self.seat_content, bg='white')
            row_frame.pack(pady=2)
            
            # Row number
            tk.Label(row_frame, text=f"{row_idx+1}", font=('Arial', 9, 'bold'), 
                    bg='white', fg='#666666', width=3).pack(side='left', padx=(0, 5))
            
            # Seat buttons
            for col_idx, seat in enumerate(row):
                if seat.strip():
                    seat_status_current = seat_status.get(seat, "available")
                    if seat in self.selected_seats:
                        seat_status_current = "selected"
                    
                    seat_color = seat_colors.get(seat_status_current, "#4CAF50")
                    
                    seat_btn = tk.Button(row_frame, text=seat, 
                                    font=('Arial', 8, 'bold'),
                                    bg=seat_color, fg='white',
                                    width=4, height=2,
                                    relief='raised', bd=1,
                                    command=lambda s=seat: self.select_seat(s))
                    seat_btn.pack(side='left', padx=1)
                    
                    self.seat_buttons[seat] = seat_btn
                    
                    # Hover effects
                    seat_btn.bind("<Enter>", lambda e, b=seat_btn: 
                                b.config(relief='sunken' if b['relief'] == 'raised' else 'raised'))
                    seat_btn.bind("<Leave>", lambda e, b=seat_btn: 
                                b.config(relief='raised' if b['relief'] == 'sunken' else 'sunken'))
                else:
                    # Empty space for aisle
                    tk.Label(row_frame, text="", width=4, bg='white').pack(side='left', padx=1)
        
        # Rear label
        tail_frame = tk.Frame(self.seat_content, bg='white')
        tail_frame.pack(pady=(10, 0))
        tk.Label(tail_frame, text="⬇️ REAR", font=('Arial', 12, 'bold'), 
                bg='white', fg='#1e3d59').pack()
        
        # Aisle label
        aisle_frame = tk.Frame(self.seat_content, bg='white')
        aisle_frame.pack(pady=(5, 0))
        tk.Label(aisle_frame, text="← AISLE →", font=('Arial', 8), 
                bg='white', fg='#666666').pack()

    def create_price_summary_card(self):
        """Create simple price summary card in right column (BASIC PRICE ONLY)"""
        self.price_card = tk.Frame(self.right_column, bg='white', relief='groove', bd=1)
        self.price_card.pack(fill='both', pady=(0, 20))
        
        # Header
        header = tk.Frame(self.price_card, bg='#1e3d59')
        header.pack(fill='x')
        tk.Label(header, text="💰 Price Summary", 
                font=('Arial', 14, 'bold'), bg='#1e3d59', fg='white', 
                padx=20, pady=12).pack(side='left')
        
        # Content frame
        self.price_content = tk.Frame(self.price_card, bg='white')
        self.price_content.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Initialize price display
        self.update_price_summary()

    def update_price_summary(self):
        """Update the price summary with current data (BASIC PRICE ONLY)"""
        # Clear existing content
        for widget in self.price_content.winfo_children():
            widget.destroy()
        
        # Calculate BASIC prices only (no tax, no fees)
        base_price = float(self.flight_data['price'].replace('RM ', '').replace(',', ''))
        total_passengers = self.adult_count + self.child_count
        total_price = base_price * total_passengers
        
        # Simple price display
        price_frame = tk.Frame(self.price_content, bg='white')
        price_frame.pack(fill='x', pady=(0, 20))
        
        # Per passenger price
        tk.Label(price_frame, text="Price per passenger:", 
                font=('Arial', 11), bg='white', fg='#666666').pack(anchor='w')
        tk.Label(price_frame, text=f"RM {base_price:,.2f}", 
                font=('Arial', 14, 'bold'), bg='white', fg='#333333').pack(anchor='w', pady=(5, 0))
        
        # Separator
        tk.Frame(self.price_content, bg='#e0e0e0', height=1).pack(fill='x', pady=15)
        
        # TOTAL PRICE (BASIC ONLY)
        total_frame = tk.Frame(self.price_content, bg='white')
        total_frame.pack(fill='x')
        tk.Label(total_frame, text="TOTAL PRICE", font=('Arial', 13, 'bold'), 
                bg='white', fg='#1e3d59').pack(side='left')
        tk.Label(total_frame, text=f"RM {total_price:,.2f}", font=('Arial', 22, 'bold'), 
                bg='white', fg='#e74c3c').pack(side='right')
        
        # Passenger summary
        passenger_frame = tk.Frame(self.price_content, bg='white')
        passenger_frame.pack(fill='x', pady=(20, 0))
        tk.Label(passenger_frame, text="Passengers", font=('Arial', 12, 'bold'), 
                bg='white', fg='#1e3d59').pack(anchor='w')
        
        passenger_text = f"{self.adult_count} Adult(s)"
        if self.child_count > 0:
            passenger_text += f", {self.child_count} Child(ren)"
        tk.Label(passenger_frame, text=passenger_text, font=('Arial', 11), 
                bg='white', fg='#666666').pack(anchor='w', pady=(5, 0))
        
        # Seat selection status
        seat_status_text = f"Selected {len(self.selected_seats)} of {total_passengers} seats"
        if len(self.selected_seats) == total_passengers and total_passengers > 0:
            seat_status_text = f"✓ All {total_passengers} seats selected"
            tk.Label(passenger_frame, text=seat_status_text, font=('Arial', 11), 
                    bg='white', fg='#27ae60').pack(anchor='w', pady=(5, 0))
        else:
            tk.Label(passenger_frame, text=seat_status_text, font=('Arial', 11), 
                    bg='white', fg='#666666').pack(anchor='w', pady=(5, 0))

    def create_action_buttons(self):
        """Create Back and Book Now buttons"""
        self.button_frame = tk.Frame(self.left_column, bg='#f5f7fa')
        self.button_frame.pack(fill='x', pady=(20, 0))
        
        # Back button
        back_btn = tk.Button(self.button_frame, text="Back to Flights", 
                           font=('Arial', 12, 'bold'), bg='#cccccc', fg='#333333',
                           command=self.return_to_main_callback, relief='flat', cursor='hand2',
                           padx=30, pady=12, bd=0)
        back_btn.pack(side='left', padx=(0, 15))
        back_btn.bind("<Enter>", lambda e: back_btn.config(bg='#bdbdbd'))
        back_btn.bind("<Leave>", lambda e: back_btn.config(bg='#cccccc'))
        
        # Book Now button
        self.book_btn = tk.Button(self.button_frame, text="BOOK NOW →", 
                                bg='#4CAF50', fg='white',  
                                font=('Arial', 14, 'bold'),
                                command=self.book_now, relief='flat', cursor='hand2', 
                                padx=40, pady=12, bd=0)
        self.book_btn.pack(side='right')
        self.book_btn.bind("<Enter>", lambda e: self.book_btn.config(bg='#66BB6A'))
        self.book_btn.bind("<Leave>", lambda e: self.book_btn.config(bg='#4CAF50'))

    def update_passenger_counts(self):
        """Update passenger counts when spinbox values change"""
        self.adult_count = self.adult_var.get()
        self.child_count = self.child_var.get()
        
        # Update total label
        self.total_label.config(text=f"Total Passengers: {self.adult_count + self.child_count}")
        
        # Update seat status label
        self.update_seat_status_label()
        
        # Update price summary
        self.update_price_summary()

    def update_seat_status_label(self):
        """Update the seat selection status label"""
        total_passengers = self.adult_count + self.child_count
        selected_count = len(self.selected_seats)
        
        if total_passengers == 0:
            self.seat_status_label.config(
                text=f"Please select number of passengers first",
                fg='#e74c3c'  # Red color for warning
            )
        else:
            if selected_count == total_passengers:
                self.seat_status_label.config(
                    text=f"✓ All {total_passengers} seats selected: {', '.join(self.selected_seats)}", 
                    fg='#27ae60'  # Green color for success
                )
            else:
                self.seat_status_label.config(
                    text=f"Selected {selected_count} of {total_passengers} required seats", 
                    fg='#666666'
                )

    def select_seat(self, seat_number):
        """Handle seat selection/deselection with popup warning if no passengers selected"""
        total_passengers = self.adult_count + self.child_count
        
        # Check if no passengers selected
        if total_passengers == 0:
            # Show popup warning
            messagebox.showwarning("No Passengers Selected", 
                                 "Please select number of passengers first before choosing seats.")
            return
        
        # Normal seat selection logic
        if seat_number in self.selected_seats:
            # Deselect seat
            self.selected_seats.remove(seat_number)
            if seat_number in self.seat_buttons:
                self.seat_buttons[seat_number].config(bg='#4CAF50')  # Back to available color
        else:
            # Select seat if not exceeding limit
            if len(self.selected_seats) < total_passengers:
                self.selected_seats.append(seat_number)
                if seat_number in self.seat_buttons:
                    self.seat_buttons[seat_number].config(bg='#2196F3')  # Selected color
            else:
                messagebox.showwarning("Seat Limit", 
                                    f"You can only select {total_passengers} seats for {self.adult_count} adults and {self.child_count} children.")
                return
        
        # Update seat status label
        self.update_seat_status_label()
        
        # Update price summary
        self.update_price_summary()

    def book_now(self):
        """Book the flight"""
        total_passengers = self.adult_count + self.child_count
        
        # Check if no passengers selected
        if total_passengers == 0:
            messagebox.showwarning("No Passengers", 
                                "Please select at least one passenger before booking.")
            return
        
        # Check if all seats are selected
        selected_count = len(self.selected_seats)
        
        if selected_count < total_passengers:
            response = messagebox.askyesno("Continue Anyway?", 
                                        f"You have selected {selected_count} out of {total_passengers} required seats. Book anyway?")
            if not response:
                return
        
        # Prepare booking data
        booking_data = self.prepare_flight_booking_data()
        
        # Close this details window FIRST
        self.return_to_main_callback()
        
        # THEN open booking confirmation window
        self.open_booking_detail_callback(booking_data)

    def prepare_flight_booking_data(self):
        """Prepare flight booking data for confirmation"""
        route_parts = self.flight_data.get('route', '').split('→')
        departure_city = "Kuala Lumpur, Malaysia"
        arrival_city = route_parts[1].strip() if len(route_parts) > 1 else ""
        
        # Handle time data safely
        time_str = self.flight_data.get('time', '08:00 - 16:00')
        time_parts = time_str.split(' - ')
        departure_time = time_parts[0] if len(time_parts) > 0 else "08:00"
        arrival_time = time_parts[1] if len(time_parts) > 1 else "16:00"
        
        base_price = float(self.flight_data['price'].replace('RM ', '').replace(',', ''))
        total_passengers = self.adult_count + self.child_count
        total_price = base_price * total_passengers  # BASIC PRICE ONLY
        
        # Generate booking ID
        booking_id = f"FLIGHT{random.randint(100000, 999999)}"
        
        # Get user info from profile
        user_email = self.email
        user_name = "Guest User"
        
        if self.profile_system:
            profile_data = self.profile_system.profile_data
            user_email = profile_data["personal_info"]["email"] or user_email
            user_name = profile_data["personal_info"]["full_name"] or user_name
        
        # Generate default passenger info
        passenger_info = []
        for i in range(total_passengers):
            passenger_type = "Adult" if i < self.adult_count else "Child"
            seat = self.selected_seats[i] if i < len(self.selected_seats) else "To be assigned"
            
            passenger_data = {
                'passenger_number': i + 1,
                'passenger_type': passenger_type,
                'title': "Mr" if passenger_type == "Adult" else "",
                'full_name': f"Passenger {i + 1}",
                'passport_number': "To be provided",
                'date_of_birth': "",
                'nationality': "Malaysian",
                'contact_number': "To be provided",
                'seat': seat
            }
            passenger_info.append(passenger_data)
        
        booking_data = {
            "booking_id": booking_id,
            "booking_type": "flight",
            "status": "pending",
            
            "flight_number": self.flight_data.get('id', 'F001'),
            "airline": self.flight_data.get('airline', 'Unknown Airline'),
            "route": self.flight_data.get('route', ''),
            "departure_city": departure_city,
            "arrival_city": arrival_city,
            "departure_date": self.departure_var.get() if self.departure_var.get() else datetime.datetime.now().strftime("%Y-%m-%d"),
            "departure_time": departure_time,
            "arrival_time": arrival_time,
            "duration": self.flight_data.get('duration', ''),
            "aircraft": self.flight_data.get('aircraft', ''),
            "stops": self.flight_data.get('stops', ''),
            
            "tickets": total_passengers,
            "adults": self.adult_count,
            "children": self.child_count,
            "passengers": passenger_info,
            "seats": ', '.join(self.selected_seats) if self.selected_seats else "To be assigned",
            "class": self.class_var.get(),
            
            "base_price": base_price,
            "ticket_price": base_price,
            "total_price": round(total_price, 2),  # BASIC PRICE ONLY
            
            # CRITICAL FIELDS FOR CORRECT PRICE DISPLAY IN CONFIRMATION PAGE
            "unit_price_per_passenger": base_price,  # Price for one passenger (RM 3750.00)
            "unit_price": base_price,  # Alias for compatibility
            "passenger_count": total_passengers,  # Total number of passengers (3)
            "total_amount": round(total_price, 2),  # Total amount (unit price × passenger count = RM 11250.00)
            
            "booking_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "is_roundtrip": self.flight_type_var.get() == "Return",
            "return_date": self.return_var.get() if self.flight_type_var.get() == "Return" else "",
            
            "user_email": user_email,
            "user_name": user_name,
            
            "item_name": f"{self.flight_data.get('airline', 'Flight')} - {self.flight_data.get('route', '')}",
            "hotel_name": self.flight_data.get('airline', 'Flight'),
            "price": total_price
        }
        
        return booking_data

    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        return "break"