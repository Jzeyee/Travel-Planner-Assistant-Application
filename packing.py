import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys
import subprocess
from datetime import datetime

class PackingApp:
    def __init__(self, root, email=None, return_home_callback=None, user_data=None):
        self.root = root
        self.email = email
        self.return_home_callback = return_home_callback
        self.user_data = user_data or {}
        self.root.attributes('-fullscreen', True)
        
        # Colors
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
        
        # Initialize packing items with categories
        self.packing_items = {
            "Travel Documents": [],
            "Clothing": [],
            "Toiletries": [],
            "Electronics": [],
            "Health & Safety": [],
            "Miscellaneous": []
        }
        
        # Default items for each category
        self.default_items = {
            "Travel Documents": ["Passport/ID", "Credit Cards/Cash", "Travel Tickets", "Hotel Reservations", "Travel Insurance"],
            "Clothing": ["T-Shirts", "Pants/Jeans", "Underwear", "Socks", "Swimwear", "Jacket", "Comfortable Shoes", "Pajamas"],
            "Toiletries": ["Toothbrush & Toothpaste", "Shampoo & Conditioner", "Soap/Body Wash", "Razor", "Deodorant", "Sunscreen", "First Aid Kit"],
            "Electronics": ["Phone Charger", "Power Bank", "Headphones", "Travel Adapter", "Camera", "Laptop/Tablet"],
            "Health & Safety": ["Prescription Medications", "Pain Relievers", "Band-Aids", "Hand Sanitizer", "Face Masks", "Insect Repellent"],
            "Miscellaneous": ["Books/Magazines", "Travel Pillow", "Water Bottle", "Snacks", "Sunglasses"]
        }
        
        # Track checked items
        self.checked_items = {}
        for category in self.default_items.keys():
            self.checked_items[category] = []
        
        # Load packing list
        self.load_packing_list()
        
        # Setup UI
        self.setup_ui()
    
    def load_packing_list(self):
        """Load packing list from file or use defaults"""
        if self.email:
            # Try to load from file
            self.load_from_file()
        else:
            # Load defaults for demo
            for category, items in self.default_items.items():
                self.packing_items[category] = items.copy()
    
    def save_packing_list(self):
        """Save packing list to file"""
        if self.email:
            self.save_to_file()
    
    def save_to_file(self):
        """Save packing list to local JSON file"""
        if not self.email:
            return
            
        try:
            # Create directory if it doesn't exist
            if not os.path.exists("user_data"):
                os.makedirs("user_data")
            
            filename = f"user_data/packing_{self.email.replace('@', '_').replace('.', '_')}.json"
            with open(filename, 'w') as f:
                json.dump({
                    'packing_items': self.packing_items,
                    'checked_items': self.checked_items,
                    'last_modified': datetime.now().isoformat()
                }, f)
            print(f"Saved packing list to {filename}")
        except Exception as e:
            print(f"Error saving to file: {e}")
    
    def load_from_file(self):
        """Load packing list from local JSON file"""
        if not self.email:
            return
            
        try:
            filename = f"user_data/packing_{self.email.replace('@', '_').replace('.', '_')}.json"
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    file_data = json.load(f)
                
                # Load packing items
                if 'packing_items' in file_data and isinstance(file_data['packing_items'], dict):
                    self.packing_items = file_data['packing_items']
                
                # Load checked items
                if 'checked_items' in file_data and isinstance(file_data['checked_items'], dict):
                    self.checked_items = file_data['checked_items']
                
                print(f"Loaded packing list from {filename}")
            else:
                # Load defaults
                for category, items in self.default_items.items():
                    self.packing_items[category] = items.copy()
        except Exception as e:
            print(f"Error loading from file: {e}")
            # Load defaults if file is corrupted
            for category, items in self.default_items.items():
                self.packing_items[category] = items.copy()
    
    def setup_ui(self):
        """Setup packing list UI"""
        self.root.title("TravelEase - Packing List")
        self.root.geometry("1400x800")
        self.root.configure(bg=self.COLORS["bg"])
        
        # Main container
        main_container = tk.Frame(self.root, bg=self.COLORS["bg"])
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_container, bg=self.COLORS["navy"], height=80)
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
        tk.Label(title_frame, text="🧳 Smart Packing List", 
                font=("Arial", 24, "bold"),
                fg="white", 
                bg=self.COLORS["navy"]).pack(pady=10)

        
        # Main content area
        content_frame = tk.Frame(main_container, bg=self.COLORS["bg"])
        content_frame.pack(fill="both", expand=True, pady=(20, 0))
        
        # Left panel - Categories and Items
        left_panel = tk.Frame(content_frame, bg=self.COLORS["bg"])
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Category selector
        self.setup_category_selector(left_panel)
        
        # Packing list container
        self.setup_packing_list_container(left_panel)
        
        # Right panel - Tips & Quick Add
        right_panel = tk.Frame(content_frame, bg=self.COLORS["bg"], width=400)
        right_panel.pack(side="right", fill="y", padx=(10, 0))
        right_panel.pack_propagate(False)
        
        # Tips container
        self.setup_tips_container(right_panel)
        
        # Quick add container
        self.setup_quick_add_container(right_panel)
        
        # Stats frame
        self.setup_stats_frame(main_container)
        
        # Display initial items
        self.display_current_category_items()
    
    def setup_category_selector(self, parent):
        """Setup category selector"""
        cat_container = tk.Frame(parent, bg="white")
        cat_container.pack(fill="x", pady=(0, 15))
        cat_container.configure(highlightbackground="#e0e0e0", highlightthickness=1)
        
        tk.Label(cat_container, text="📂 Categories", 
                font=("Arial", 18, "bold"),
                bg="white", 
                fg=self.COLORS["navy"]).pack(anchor="w", padx=25, pady=20)
        
        # Category buttons
        cat_buttons_frame = tk.Frame(cat_container, bg="white")
        cat_buttons_frame.pack(fill="x", padx=25, pady=(0, 25))
        
        categories = list(self.packing_items.keys())
        self.category_buttons = []
        self.current_category = categories[0]
        
        for i, category in enumerate(categories):
            btn = tk.Button(cat_buttons_frame,
                          text=category,
                          command=lambda c=category: self.switch_category(c),
                          font=("Arial", 11),
                          bg=self.COLORS["light_gray"] if category != self.current_category else self.COLORS["dark_orange"],
                          fg=self.COLORS["text"] if category != self.current_category else "white",
                          activebackground=self.COLORS["dark_orange"] if category != self.current_category else self.COLORS["light_orange"],
                          activeforeground="white" if category != self.current_category else self.COLORS["text"],
                          bd=0,
                          cursor="hand2",
                          padx=15,
                          pady=8)
            btn.grid(row=i//3, column=i%3, padx=5, pady=5, sticky="ew")
            self.category_buttons.append(btn)
        
        # Configure grid columns
        for i in range(3):
            cat_buttons_frame.grid_columnconfigure(i, weight=1)
    
    def setup_packing_list_container(self, parent):
        """Setup packing list container"""
        list_container = tk.Frame(parent, bg="white")
        list_container.pack(fill="both", expand=True)
        list_container.configure(highlightbackground="#e0e0e0", highlightthickness=1)
        
        # Packing list header
        self.list_header = tk.Frame(list_container, bg=self.COLORS["navy"], height=60)
        self.list_header.pack(fill="x")
        self.list_header.pack_propagate(False)
        
        self.category_title = tk.Label(self.list_header, 
                                      text=f"My {self.current_category} Items",
                                      font=("Arial", 18, "bold"),
                                      bg=self.COLORS["navy"], 
                                      fg="white")
        self.category_title.pack(side="left", padx=25, pady=20)
        
        # Item count
        self.item_count_label = tk.Label(self.list_header, 
                                        text="0 items",
                                        font=("Arial", 12),
                                        bg=self.COLORS["navy"], 
                                        fg="#ffffff")
        self.item_count_label.pack(side="right", padx=25)
        
        # Add item section
        add_section = tk.Frame(list_container, bg="white", height=80)
        add_section.pack(fill="x", pady=(15, 0))
        add_section.pack_propagate(False)
        
        add_inner = tk.Frame(add_section, bg="white")
        add_inner.pack(pady=20, padx=25)
        
        # Entry with placeholder
        self.new_item_var = tk.StringVar()
        self.item_entry = tk.Entry(add_inner, 
                                  textvariable=self.new_item_var,
                                  font=("Arial", 12),
                                  width=35,
                                  bd=1,
                                  relief="solid")
        self.item_entry.pack(side="left", padx=(0, 10))
        self.item_entry.insert(0, "Add new item...")
        self.item_entry.bind("<FocusIn>", self.on_entry_focus_in)
        self.item_entry.bind("<FocusOut>", self.on_entry_focus_out)
        self.item_entry.bind("<Return>", lambda e: self.add_item())
        
        # Add button
        add_btn = tk.Button(add_inner, 
                           text="+ Add",
                           command=self.add_item,
                           font=("Arial", 12, "bold"),
                           bg=self.COLORS["dark_orange"],
                           fg="white",
                           activebackground=self.COLORS["light_orange"],
                           bd=0,
                           cursor="hand2",
                           padx=20,
                           pady=8)
        add_btn.pack(side="left")
        
        # Items list with scrollbar
        list_items_frame = tk.Frame(list_container, bg="white")
        list_items_frame.pack(fill="both", expand=True, padx=25, pady=(0, 25))
        
        # Create scrollable canvas
        self.canvas = tk.Canvas(list_items_frame, bg="white", highlightthickness=0)
        scrollbar = tk.Scrollbar(list_items_frame, orient="vertical", command=self.canvas.yview)
        self.items_container = tk.Frame(self.canvas, bg="white")
        
        self.canvas.create_window((0, 0), window=self.items_container, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind events for scrolling
        self.items_container.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def setup_tips_container(self, parent):
        """Setup tips container"""
        tips_container = tk.Frame(parent, bg="white")
        tips_container.pack(fill="x", pady=(0, 15))
        tips_container.configure(highlightbackground="#e0e0e0", highlightthickness=1)
        
        tk.Label(tips_container, text="📝 Packing Tips", 
                font=("Arial", 18, "bold"),
                bg="white", 
                fg=self.COLORS["navy"]).pack(anchor="w", padx=25, pady=20)
        
        # Tips content
        tips_content = tk.Frame(tips_container, bg="white")
        tips_content.pack(fill="both", expand=True, padx=25, pady=(0, 25))
        
        tips = [
            ("✈️ Flight Essentials", "Keep passport, tickets, and boarding passes in an easily accessible place"),
            ("💊 Health & Safety", "Pack medications in original containers and carry doctor's prescriptions"),
            ("👕 Clothing Strategy", "Roll clothes to save space and reduce wrinkles"),
            ("🔌 Electronics", "Use a cable organizer bag for all chargers and cables"),
            ("🧴 TSA Compliance", "Pack liquids in clear, quart-sized bags (3-1-1 rule)"),
            ("📱 Digital Copies", "Take photos of important documents and save them in the cloud")
        ]
        
        for tip_title, tip_desc in tips:
            tip_card = tk.Frame(tips_content, bg=self.COLORS["light_gray"])
            tip_card.pack(fill="x", pady=8)
            
            tk.Label(tip_card, text=tip_title, 
                    font=("Arial", 12, "bold"),
                    bg=self.COLORS["light_gray"], 
                    fg=self.COLORS["navy"]).pack(anchor="w", padx=15, pady=(10, 5))
            tk.Label(tip_card, text=tip_desc, 
                    font=("Arial", 10),
                    bg=self.COLORS["light_gray"], 
                    fg=self.COLORS["text_light"],
                    wraplength=350,
                    justify="left").pack(anchor="w", padx=15, pady=(0, 10))
    
    def setup_quick_add_container(self, parent):
        """Setup quick add container with horizontal scrolling"""
        quick_container = tk.Frame(parent, bg="white")
        quick_container.pack(fill="x")
        quick_container.configure(highlightbackground="#e0e0e0", highlightthickness=1)
        
        tk.Label(quick_container, text="⚡ Quick Add", 
                font=("Arial", 18, "bold"),
                bg="white", 
                fg=self.COLORS["navy"]).pack(anchor="w", padx=25, pady=20)
        
        # Category selector for quick add
        quick_cat_frame = tk.Frame(quick_container, bg="white")
        quick_cat_frame.pack(fill="x", padx=25, pady=(0, 10))
        
        tk.Label(quick_cat_frame, text="Add to:", 
                font=("Arial", 10, "bold"),
                bg="white", 
                fg=self.COLORS["text"]).pack(side="left", padx=(0, 10))
        
        self.quick_cat_var = tk.StringVar(value=self.current_category)
        quick_cat_menu = ttk.Combobox(quick_cat_frame,
                                     textvariable=self.quick_cat_var,
                                     values=list(self.packing_items.keys()),
                                     state="readonly",
                                     font=("Arial", 10),
                                     width=15)
        quick_cat_menu.pack(side="left")
        
        # Container for the horizontal scrollable area
        scroll_container = tk.Frame(quick_container, bg="white")
        scroll_container.pack(fill="x", padx=25, pady=(0, 25))
        
        # Create horizontal scrollable canvas
        self.quick_canvas = tk.Canvas(scroll_container, bg="white", height=120, highlightthickness=0)
        h_scrollbar = tk.Scrollbar(scroll_container, orient="horizontal", command=self.quick_canvas.xview)
        
        self.quick_items_container = tk.Frame(self.quick_canvas, bg="white")
        
        self.quick_canvas.create_window((0, 0), window=self.quick_items_container, anchor="nw")
        self.quick_canvas.configure(xscrollcommand=h_scrollbar.set)
        
        # Bind events for scrolling
        self.quick_items_container.bind("<Configure>", self.on_quick_frame_configure)
        
        self.quick_canvas.pack(side="top", fill="x")
        h_scrollbar.pack(side="bottom", fill="x")
        
        self.update_quick_add_items()
    
    def setup_stats_frame(self, parent):
        """Setup statistics frame"""
        self.stats_frame = tk.Frame(parent, bg=self.COLORS["white"], height=50)
        self.stats_frame.pack(fill="x", pady=(15, 0))
        self.stats_frame.pack_propagate(False)
        
        stats_inner = tk.Frame(self.stats_frame, bg=self.COLORS["white"])
        stats_inner.pack(expand=True, fill="both")
        
        self.update_stats()
    
    def switch_category(self, category):
        """Switch to a different category"""
        self.current_category = category
        self.category_title.config(text=f"My {category} Items")
        self.quick_cat_var.set(category)
        
        # Update button styles
        for btn in self.category_buttons:
            if btn.cget("text") == category:
                btn.config(bg=self.COLORS["dark_orange"], fg="white")
            else:
                btn.config(bg=self.COLORS["light_gray"], fg=self.COLORS["text"])
        
        self.display_current_category_items()
        self.update_quick_add_items()
    
    def update_quick_add_items(self):
        """Update quick add items based on current category"""
        # Clear existing items
        for widget in self.quick_items_container.winfo_children():
            widget.destroy()
        
        # Get suggested items for current category (exclude already added items)
        suggested_items = []
        default_items = self.default_items.get(self.current_category, [])
        current_items = self.packing_items.get(self.current_category, [])
        
        for item in default_items:
            if item not in current_items:
                suggested_items.append(item)
        
        # Add some generic items if needed
        if len(suggested_items) < 4:
            generic_items = ["Travel Lock", "Laundry Bag", "Extra Batteries", "Travel Journal", 
                           "Portable Umbrella", "Travel Towel", "Water Purifier", "Ear Plugs",
                           "Sleep Mask", "Travel Insurance Docs", "International Driver's License"]
            for item in generic_items:
                if item not in current_items and len(suggested_items) < 12:
                    suggested_items.append(item)
        
        # Create buttons in a horizontal layout
        for i, item in enumerate(suggested_items[:12]):  # Show max 12 items
            btn_frame = tk.Frame(self.quick_items_container, bg="white")
            btn_frame.pack(side="left", padx=5, pady=5)
            
            btn = tk.Button(btn_frame,
                          text=f"+ {item}",
                          command=lambda i=item: self.add_quick_item(i),
                          font=("Arial", 10),
                          bg=self.COLORS["light_orange"],
                          fg="white",
                          activebackground=self.COLORS["dark_orange"],
                          bd=0,
                          cursor="hand2",
                          padx=15,
                          pady=8,
                          wraplength=150,  # Allow text to wrap
                          justify="center",
                          height=2,  # Make buttons taller for wrapped text
                          width=15)  # Set fixed width
            btn.pack()
    
    def display_current_category_items(self):
        """Display items for current category"""
        # Clear existing items
        for widget in self.items_container.winfo_children():
            widget.destroy()
        
        self.checkbox_vars = []
        items = self.packing_items.get(self.current_category, [])
        
        # Display items
        for i, item in enumerate(items):
            self.create_item_widget(i, item)
        
        # Update item count
        self.item_count_label.config(text=f"{len(items)} items")
        self.update_stats()
    
    def create_item_widget(self, index, item):
        """Create a single packing item widget"""
        item_frame = tk.Frame(self.items_container, bg="white")
        item_frame.pack(fill="x", pady=4)
        item_frame.configure(highlightbackground="#e8e8e8", highlightthickness=1)
        
        # Checkbox
        var = tk.BooleanVar()
        # Check if this item is already marked as packed
        initial_state = item in self.checked_items.get(self.current_category, [])
        var.set(initial_state)
        self.checkbox_vars.append(var)
        
        checkbox_label = tk.Label(item_frame, 
                                 text="☑" if initial_state else "☐",
                                 font=("Arial", 14),
                                 bg="white",
                                 fg=self.COLORS["success"] if initial_state else self.COLORS["text_light"],
                                 cursor="hand2")
        checkbox_label.pack(side="left", padx=(15, 10))
        checkbox_label.bind("<Button-1>", 
                          lambda e, idx=index, v=var, it=item: self.toggle_checkbox(idx, v, it))
        
        # Item label
        label = tk.Label(item_frame, 
                        text=item, 
                        font=("Arial", 12),
                        bg="white", 
                        fg=self.COLORS["text"],
                        anchor="w")
        label.pack(side="left", fill="x", expand=True, padx=10, pady=12)
        
        # Delete button
        delete_btn = tk.Label(item_frame,
                             text="✕",
                             font=("Arial", 12),
                             bg="white",
                             fg=self.COLORS["text_light"],
                             cursor="hand2")
        delete_btn.pack(side="right", padx=15)
        delete_btn.bind("<Button-1>", lambda e, idx=index: self.remove_item(idx))
        
        # Hover effects
        def on_enter(e):
            item_frame.configure(bg=self.COLORS["light_gray"])
            for child in item_frame.winfo_children():
                child.configure(bg=self.COLORS["light_gray"])
            delete_btn.configure(fg=self.COLORS["danger"])
        
        def on_leave(e):
            item_frame.configure(bg="white")
            for child in item_frame.winfo_children():
                child.configure(bg="white")
            delete_btn.configure(fg=self.COLORS["text_light"])
        
        item_frame.bind("<Enter>", on_enter)
        item_frame.bind("<Leave>", on_leave)
        label.bind("<Enter>", on_enter)
        label.bind("<Leave>", on_leave)
        delete_btn.bind("<Enter>", on_enter)
        delete_btn.bind("<Leave>", on_leave)
        
        # Make entire row clickable for checkbox
        for widget in [item_frame, label]:
            widget.bind("<Button-1>", 
                       lambda e, idx=index, v=var, it=item: self.toggle_checkbox(idx, v, it))
    
    def toggle_checkbox(self, index, var, item):
        """Toggle checkbox state and update checked items"""
        var.set(not var.get())
        
        # Find the checkbox label in the widget tree
        item_frame = self.items_container.winfo_children()[index]
        checkbox_label = item_frame.winfo_children()[0]
        
        if var.get():
            checkbox_label.config(text="☑", fg=self.COLORS["success"])
            # Add to checked items
            if item not in self.checked_items[self.current_category]:
                self.checked_items[self.current_category].append(item)
        else:
            checkbox_label.config(text="☐", fg=self.COLORS["text_light"])
            # Remove from checked items
            if item in self.checked_items[self.current_category]:
                self.checked_items[self.current_category].remove(item)
        
        self.save_packing_list()  # Auto-save when checking/unchecking
        self.update_stats()
    
    def update_stats(self):
        """Update statistics display"""
        # Clear existing stats
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        stats_inner = tk.Frame(self.stats_frame, bg=self.COLORS["white"])
        stats_inner.pack(expand=True, fill="both")
        
        # Calculate totals
        total_items = 0
        packed_items = 0
        
        for category, items in self.packing_items.items():
            total_items += len(items)
            packed_items += len(self.checked_items.get(category, []))
        
        # Calculate percentages
        packed_percentage = (packed_items / total_items * 100) if total_items > 0 else 0
        
        # Display stats
        tk.Label(stats_inner, text=f"📦 Categories: {len(self.packing_items)}",
                font=("Arial", 11),
                bg=self.COLORS["white"],
                fg=self.COLORS["text"]).pack(side="left", padx=20)
        
        tk.Label(stats_inner, text=f"📋 Total Items: {total_items}",
                font=("Arial", 11),
                bg=self.COLORS["white"],
                fg=self.COLORS["text"]).pack(side="left", padx=20)
        
        tk.Label(stats_inner, text=f"✅ Packed: {packed_items}/{total_items} ({packed_percentage:.0f}%)",
                font=("Arial", 11),
                bg=self.COLORS["white"],
                fg=self.COLORS["success"]).pack(side="left", padx=20)
        
        # Summary List Button
        summary_btn = tk.Button(stats_inner, 
                               text="📊 Summary List",
                               command=self.show_summary_list,
                               font=("Arial", 11, "bold"),
                               bg=self.COLORS["info"],
                               fg="white",
                               bd=0,
                               cursor="hand2",
                               padx=15,
                               pady=5)
        summary_btn.pack(side="right", padx=20)
        
        # Auto-save notice
        if self.email:
            save_label = tk.Label(stats_inner, 
                                 text="💾 Auto-saved",
                                 font=("Arial", 9),
                                 bg=self.COLORS["white"],
                                 fg=self.COLORS["success"])
            save_label.pack(side="right", padx=5)
    
    def on_frame_configure(self, event):
        """Update scrollregion when frame size changes"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        """Update canvas window width when canvas size changes"""
        self.canvas.itemconfig(1, width=event.width)
    
    def on_quick_frame_configure(self, event):
        """Update quick items scrollregion when frame size changes"""
        self.quick_canvas.configure(scrollregion=self.quick_canvas.bbox("all"))
    
    def on_entry_focus_in(self, event):
        """Handle entry focus in"""
        if self.item_entry.get() == "Add new item...":
            self.item_entry.delete(0, tk.END)
            self.item_entry.configure(fg="black")
    
    def on_entry_focus_out(self, event):
        """Handle entry focus out"""
        if not self.item_entry.get():
            self.item_entry.insert(0, "Add new item...")
            self.item_entry.configure(fg="gray")
    
    def add_item(self):
        """Add new item to packing list"""
        item = self.new_item_var.get().strip()
        if item and item != "Add new item...":
            if self.current_category not in self.packing_items:
                self.packing_items[self.current_category] = []
            
            self.packing_items[self.current_category].append(item)
            self.save_packing_list()
            self.new_item_var.set("")
            self.item_entry.delete(0, tk.END)
            self.item_entry.insert(0, "Add new item...")
            self.item_entry.configure(fg="gray")
            self.display_current_category_items()
            self.update_quick_add_items()
    
    def add_quick_item(self, item):
        """Add quick item to packing list"""
        category = self.quick_cat_var.get()
        
        if category not in self.packing_items:
            self.packing_items[category] = []
        
        if item not in self.packing_items[category]:
            self.packing_items[category].append(item)
            self.save_packing_list()
            
            # If we're viewing this category, update display
            if category == self.current_category:
                self.display_current_category_items()
            
            self.update_quick_add_items()
    
    def remove_item(self, index):
        """Remove item from packing list"""
        items = self.packing_items.get(self.current_category, [])
        if 0 <= index < len(items):
            item = items[index]
            if messagebox.askyesno("Remove Item", 
                                 f"Remove '{item}' from your {self.current_category} list?"):
                # Remove from checked items if it's there
                if item in self.checked_items.get(self.current_category, []):
                    self.checked_items[self.current_category].remove(item)
                
                items.pop(index)
                self.save_packing_list()
                self.display_current_category_items()
                self.update_quick_add_items()
    
    def show_summary_list(self):
        """Show packing list summary in a new window"""
        summary_window = tk.Toplevel(self.root)
        summary_window.title("Packing List Summary")
        summary_window.geometry("800x600")
        summary_window.configure(bg="white")
        summary_window.resizable(True, True)
        
        # Center the window
        summary_window.transient(self.root)
        summary_window.grab_set()
        
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 400
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 300
        summary_window.geometry(f"+{x}+{y}")
        
        # Header
        header = tk.Frame(summary_window, bg=self.COLORS["navy"], height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(header, text="📊 Packing List Summary", 
                font=("Arial", 20, "bold"),
                fg="white", 
                bg=self.COLORS["navy"]).pack(pady=20)
        
        # Content frame with scrollbar
        content_frame = tk.Frame(summary_window, bg="white")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create scrollable canvas
        canvas = tk.Canvas(content_frame, bg="white", highlightthickness=0)
        scrollbar = tk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Calculate totals
        total_items = 0
        packed_items = 0
        
        for category, items in self.packing_items.items():
            total_items += len(items)
            packed_items += len(self.checked_items.get(category, []))
        
        packed_percentage = (packed_items / total_items * 100) if total_items > 0 else 0
        
        # Progress bar frame
        progress_frame = tk.Frame(scrollable_frame, bg="white")
        progress_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(progress_frame, text="Overall Packing Progress", 
                font=("Arial", 16, "bold"),
                bg="white", 
                fg=self.COLORS["navy"]).pack(anchor="w", pady=(0, 10))
        
        # Progress bar
        progress_bar_frame = tk.Frame(progress_frame, bg="#e0e0e0", height=20)
        progress_bar_frame.pack(fill="x", pady=5)
        progress_bar_frame.pack_propagate(False)
        
        # Filled portion
        fill_width = int(300 * (packed_percentage / 100))
        progress_fill = tk.Frame(progress_bar_frame, bg=self.COLORS["success"], width=fill_width)
        progress_fill.pack(side="left", fill="y")
        
        # Percentage label
        tk.Label(progress_frame, text=f"{packed_percentage:.1f}% Complete ({packed_items}/{total_items} items)",
                font=("Arial", 12),
                bg="white", 
                fg=self.COLORS["text"]).pack(anchor="w", pady=(5, 0))
        
        # Category breakdown
        tk.Label(scrollable_frame, text="Category Breakdown", 
                font=("Arial", 16, "bold"),
                bg="white", 
                fg=self.COLORS["navy"]).pack(anchor="w", pady=(0, 10))
        
        # Create summary for each category
        for category, items in self.packing_items.items():
            if items:  # Only show categories with items
                cat_frame = tk.Frame(scrollable_frame, bg="white")
                cat_frame.pack(fill="x", pady=8)
                cat_frame.configure(highlightbackground="#e8e8e8", highlightthickness=1, relief="solid")
                
                # Category header
                cat_header = tk.Frame(cat_frame, bg=self.COLORS["light_gray"])
                cat_header.pack(fill="x", pady=1)
                
                tk.Label(cat_header, text=f"📁 {category}", 
                        font=("Arial", 14, "bold"),
                        bg=self.COLORS["light_gray"], 
                        fg=self.COLORS["navy"]).pack(side="left", padx=15, pady=10)
                
                cat_packed = len(self.checked_items.get(category, []))
                cat_total = len(items)
                cat_percentage = (cat_packed / cat_total * 100) if cat_total > 0 else 0
                
                tk.Label(cat_header, text=f"{cat_packed}/{cat_total} items ({cat_percentage:.0f}%)", 
                        font=("Arial", 12),
                        bg=self.COLORS["light_gray"], 
                        fg=self.COLORS["success"] if cat_percentage == 100 else self.COLORS["warning"] if cat_percentage > 0 else self.COLORS["text_light"]).pack(side="right", padx=15)
                
                # Items list
                items_frame = tk.Frame(cat_frame, bg="white")
                items_frame.pack(fill="x", padx=15, pady=10)
                
                for i, item in enumerate(items):
                    item_row = tk.Frame(items_frame, bg="white")
                    item_row.pack(fill="x", pady=2)
                    
                    # Checkbox icon
                    checkbox_icon = "✅" if item in self.checked_items.get(category, []) else "◻️"
                    tk.Label(item_row, text=checkbox_icon,
                            font=("Arial", 12),
                            bg="white",
                            fg=self.COLORS["success"] if checkbox_icon == "✅" else self.COLORS["text_light"]).pack(side="left", padx=(0, 10))
                    
                    tk.Label(item_row, text=item, 
                            font=("Arial", 11),
                            bg="white", 
                            fg=self.COLORS["text"] if checkbox_icon == "◻️" else self.COLORS["text_light"],
                            wraplength=600,
                            justify="left").pack(side="left", anchor="w")
        
        # Recommendations section
        tk.Label(scrollable_frame, text="📋 Recommendations", 
                font=("Arial", 16, "bold"),
                bg="white", 
                fg=self.COLORS["navy"]).pack(anchor="w", pady=(20, 10))
        
        recommendations = []
        
        # Check for important items
        important_items = {
            "Travel Documents": ["Passport/ID", "Travel Tickets"],
            "Health & Safety": ["Prescription Medications", "First Aid Kit"]
        }
        
        for category, important_list in important_items.items():
            for item in important_list:
                if item in self.packing_items.get(category, []) and item not in self.checked_items.get(category, []):
                    recommendations.append(f"❗ Remember to pack: {item} ({category})")
        
        # Check for empty categories
        for category, items in self.packing_items.items():
            if not items:
                recommendations.append(f"📝 Consider adding items to: {category}")
        
        if not recommendations:
            recommendations.append("🎉 Great job! Your packing list looks complete.")
        
        for rec in recommendations:
            rec_frame = tk.Frame(scrollable_frame, bg=self.COLORS["light_gray"])
            rec_frame.pack(fill="x", pady=4)
            
            tk.Label(rec_frame, text=rec, 
                    font=("Arial", 11),
                    bg=self.COLORS["light_gray"], 
                    fg=self.COLORS["text"],
                    wraplength=700,
                    justify="left").pack(anchor="w", padx=10, pady=8)
        
        # Simple Close button only
        close_btn = tk.Button(scrollable_frame,
                             text="Close",
                             command=summary_window.destroy,
                             font=("Arial", 11, "bold"),
                             bg=self.COLORS["navy"],
                             fg="white",
                             bd=0,
                             cursor="hand2",
                             padx=40,
                             pady=10)
        close_btn.pack(pady=20)
        
        # Configure scrollable area
        scrollable_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
        canvas.config(width=760, height=400)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel for scrolling
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        # Save auto-save timestamp
        self.save_packing_list()
    
    def go_home(self):
        """Return to home page"""
        self.save_packing_list()
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
                        "🧳 Packing List - Plan what to pack",
                        "🗺️ Itinerary - Plan your daily activities",
                        "🏨 Accommodation - Find and book hotels",
                        "🍽️ Restaurants - Discover local dining",
                        "🚗 Transportation - Book rides and tickets"
                    ]
                    
                    for feature in features:
                        tk.Label(content, text=feature, 
                                font=("Arial", 14),
                                bg=self.COLORS["bg"],
                                fg=self.COLORS["text"]).pack(anchor="w", pady=8)
                    
                    packing_btn = tk.Button(content,
                                          text="🧳 Open Packing List",
                                          command=lambda: self.open_packing(home_window),
                                          font=("Arial", 14, "bold"),
                                          bg=self.COLORS["dark_orange"],
                                          fg="white",
                                          bd=0,
                                          cursor="hand2",
                                          padx=30,
                                          pady=15)
                    packing_btn.pack(pady=40)
                    
                    home_window.mainloop()
    
    def open_packing(self, home_window):
        """Open packing list from home window"""
        home_window.destroy()
        root = tk.Tk()
        app = PackingApp(root, email=self.email, user_data=self.user_data)
        root.mainloop()


# For standalone testing
if __name__ == "__main__":
    root = tk.Tk()
    app = PackingApp(root, "test@example.com")
    root.mainloop()