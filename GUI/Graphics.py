import tkinter as tk
from tkinter import ttk
import Controll 
import StagedProgressBar as StagedProgressBar
import time
from PIL import Image, ImageTk
import uuid


class GameUI:
    def __init__(self, resolution):
        self.root = tk.Tk()

        self.root.title("Interactive Map")
        self.root.geometry(resolution)

        self.controller = Controll.GameControll()

        self.turn_var = tk.StringVar(value="Turn: 0")
        self.turn_label = tk.Label(
            self.root,
            textvariable=self.turn_var,
            font=("Arial", 12, "bold"),
            bg="#F0F0F0",
            anchor="center",
            padx=10,
            pady=6
        )
        self.turn_label.pack(side=tk.TOP, fill=tk.X)

        self.map_obj = ClickableMap(self.root, "./map.png", self.controller)
        self.player_handler =  PlayerHandler(self.root, self.controller, self.map_obj)
        self.map_obj.draw_full_state(self.controller.state)
        self._build_menu(self.root)

        self.root.mainloop()
    def draw_game_state(self, game_state):
        self.turn_var.set(f"{self.controller.state.turn}")
        self.player_handler.update_tickets(game_state)
        self.map_obj.draw_full_state(game_state)

    def wait_for_input(player):
        pass

    def start_game(self):
        #self.controller.start_game()
        self.player_handler.create_live_game_panles()



    def _build_menu(self, root: tk.Tk) -> tk.Menu:
        menubar = tk.Menu(root)

        # -------- Game --------
        game_menu = tk.Menu(menubar, tearoff=False)
        game_menu.add_command(label="New Game", command=lambda: None)
        game_menu.add_command(label="Start Game", command=self.start_game)
        game_menu.add_separator()
        game_menu.add_command(label="Save", command=lambda: None)
        game_menu.add_command(label="Load", command=lambda: None)
        game_menu.add_separator()
        game_menu.add_command(label="Exit", command=root.destroy)

        menubar.add_cascade(label="Game", menu=game_menu)

        # -------- Options --------
        options_menu = tk.Menu(menubar, tearoff=False)
        options_menu.add_command(label="Reset Zoom", command=lambda: None)
        options_menu.add_command(label="Toggle Markers", command=lambda: None)
        options_menu.add_separator()
        options_menu.add_command(label="Settings", command=lambda: None)

        menubar.add_cascade(label="Options", menu=options_menu)

        root.config(menu=menubar)
        return menubar
        


class ClickableMap:
    def __init__(self, root, image_path, controller):
        self.root = root
        self.image_path = image_path
        self.controller = controller
        self.colours = ["black", "red", "blue", "green", "brown", "pink"]

        # Load original image
        self.img = Image.open(image_path)
        self.original_width, self.original_height = self.img.size

        # Canvas fills the window
        self.canvas = tk.Canvas(root, bg="white", cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Image-related state
        self.imgobj = None
        self.image_id = None
        self.display_width = None
        self.display_height = None
        self.players = None
        self.offset_x = 0
        self.offset_y = 0
        self.scale = 0
        self.original_diameter_of_marker = 45

        # Coordinate label
        self.coord_label = tk.Label(
            root,
            text="Click on the map to get coordinates",
            font=("Arial", 12),
        )
        self.coord_label.pack(side=tk.BOTTOM, pady=5)

        self.click_coordinates = []

        # Bind events
        self.canvas.bind("<Button-1>", self.on_map_click)
        self.canvas.bind("<Configure>", self.on_resize)

    # ---------------- RESIZE & DRAW ---------------- #

    def on_resize(self, event):
        canvas_w = event.width
        canvas_h = event.height

        # Keep aspect ratio
        self.scale = min(
            canvas_w / self.original_width,
            canvas_h / self.original_height,
        )

        self.display_width = int(self.original_width * self.scale)
        self.display_height = int(self.original_height * self.scale)

        resized = self.img.resize(
            (self.display_width, self.display_height),
            Image.Resampling.LANCZOS,
        )
        self.imgobj = ImageTk.PhotoImage(resized)

        # Center offsets
        self.offset_x = (canvas_w - self.display_width) // 2
        self.offset_y = (canvas_h - self.display_height) // 2

        # Draw or update image
        if self.image_id is None:
            self.image_id = self.canvas.create_image(
                canvas_w // 2,
                canvas_h // 2,
                image=self.imgobj,
                anchor="center",
            )
        else:
            self.canvas.itemconfig(self.image_id, image=self.imgobj)
            self.canvas.coords(
                self.image_id,
                canvas_w // 2,
                canvas_h // 2,
            )
        self.clear_markers()
        # Redraw existing markers after resize
        for coord in self.click_coordinates:
            try:
                x, y = coord
            except Exception:
                continue
            #self.draw_marker(x, y)
        self.draw_full_state(self.controller.state)

    # ---------------- CLICK HANDLING ---------------- #

    def on_map_click(self, event):
        cx, cy = event.x, event.y

        # Check if click is inside the image
        if not (
            self.offset_x <= cx <= self.offset_x + self.display_width
            and self.offset_y <= cy <= self.offset_y + self.display_height
        ):
            return

        # Convert to image-local coordinates
        img_x = cx - self.offset_x
        img_y = cy - self.offset_y

        # Convert to original image coordinates
        original_x = int((img_x / self.display_width) * self.original_width)
        original_y = int((img_y / self.display_height) * self.original_height)

        self.click_coordinates.append((original_x, original_y))

        clicked_station = self.controller.select_station(original_x, original_y)
        if len(clicked_station) != 0:
            self.coord_label.config(text=f"Clicked on station: {clicked_station[0].id}")


        #self.draw_marker(original_x, original_y)

    # ---------------- MARKERS ---------------- #

    def draw_full_state(self, state):
        self.clear_markers()
        players = state.player_locs
        for index in range(len(players)):
            self.draw_marker_on_station(players[index], self.colours[index])
            

    def draw_marker_on_station(self, station_number, colour):
        coords = self.controller.get_station_coords(station_number)
        self.draw_marker(coords[0], coords[1], colour)

    def draw_marker(self, x, y, color="red"):
        # Convert original image coordinates (x,y) to canvas coordinates
        if self.display_width is None or self.display_height is None:
            return

        # fractional mapping to avoid integer-division errors
        canvas_x = int(self.offset_x + (x / float(self.original_width)) * self.display_width)
        canvas_y = int(self.offset_y + (y / float(self.original_height)) * self.display_height)

        # scale marker size with current display scale
        try:
            radius = max(3, int((self.original_diameter_of_marker * self.scale) / 2))
        except Exception:
            radius = max(3, int(self.original_diameter_of_marker / 2))

        oval_id = self.canvas.create_oval(
            canvas_x - radius,
            canvas_y - radius,
            canvas_x + radius,
            canvas_y + radius,
            fill=color,
            outline="black",
            width=max(1, int(2 * self.scale)), tags=('marker'))

        # ensure marker is above the image
        try:
            self.canvas.tag_raise(oval_id)
        except Exception:
            pass
        return oval_id

    # ---------------- UTILS ---------------- #

    def clear_markers(self):
        self.canvas.delete('marker')

    def get_all_coordinates(self):
        return self.click_coordinates
    
class PlayerHandler:

    def __init__(self, root, controller, map_obj):
        self.controller = controller
        self.players = controller.players
        self.max_players = 6
        self.colours = map_obj.colours
        self.map_obj = map_obj
        self.starting_strings = []
        
        # Store radio variables for each player
        self.radio_vars = {}  # player_index -> tk.IntVar

        self.frame = tk.Frame(root, bg="lightblue", height=80)
        self.frame.pack(side=tk.BOTTOM, fill=tk.X)

        for i in range(6):
            self.frame.columnconfigure(i, weight=1, uniform="equal")


        
        self.add_player()
        self.add_player()
        self.add_player()

        self.create_panels()

    def create_panels(self):
        """Create or update all player panels"""
        # Clear existing frames
        for widget in self.frame.winfo_children():
            widget.destroy()
        
        self.subframes = []
        self.comboboxes = []
        self.player_widgets = []
        
        for i in range(self.max_players):
            # Create subframe
            subframe = tk.Frame(self.frame, bg="white", 
                               relief=tk.RAISED, borderwidth=2)
            subframe.grid(row=0, column=i, sticky="nsew", padx=2, pady=2)
            self.subframes.append(subframe)
            
            # Configure subframe grid
            subframe.grid_rowconfigure(0, weight=0)  # Top (name/button)
            subframe.grid_rowconfigure(1, weight=1)  # Middle (content)
            subframe.grid_rowconfigure(2, weight=0)  # Bottom (combobox/empty)
            
            # CASE 1: This position has a player
            if i < len(self.controller.players):
                player = self.controller.players[i]
                self.create_player_panel(subframe, i)
            
            # CASE 2: Next available spot - "Add Player" button
            elif i == len(self.controller.players):
                self.create_add_player_button(subframe, i)
            
            # CASE 3: Future empty spots - blank frame
            else:
                self.create_blank_frame(subframe, i)

    def create_live_game_panles(self):
        """Create panels to display information of players"""
        for widget in self.frame.winfo_children():
            widget.destroy()

        self.subframes = []
        self.comboboxes = []
        self.player_widgets = []

        for i in range(self.max_players):
            subframe = tk.Frame(self.frame, bg="white", relief=tk.RAISED, borderwidth=2)
            subframe.grid(row=0, column=i, sticky="nsew", padx=2, pady=2)
            self.subframes.append(subframe)

            # IMPORTANT: allow internal grid content to stretch horizontally
            subframe.grid_columnconfigure(0, weight=1)
            subframe.grid_columnconfigure(1, weight=0)

            # Make the content row expandable (bars live on row=1 in panels)
            subframe.grid_rowconfigure(0, weight=0)
            subframe.grid_rowconfigure(1, weight=1)

            if i < len(self.controller.players):
                if i == 0:
                    self.create_mister_x_info_panel(subframe, i)
                else:
                    self.create_detective_info_panel(subframe, i)
            else:
                self.create_blank_frame(subframe, i)

    def create_detective_info_panel(self, frame, index):
        """Display available move tickets for a detective (Taxi/Bus/Tube)."""

        # Allow this frame's column 0 to stretch
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        name_label = tk.Label(
            frame,
            text=self.players[index][0],
            font=("Arial", 11, "bold"),
            bg=self.colours[index],
            fg="white"
        )
        name_label.grid(row=0, column=0, sticky="ew", padx=(10, 10), pady=(8, 0))

        length = 150
        trough_color = "#E6E6E6"
        row_padding = 6
        bar_thickness = 6

        t1, t2, t3 = "Taxi", "Bus", "Tube"
        c1, c2, c3 = "yellow", "green", "red"
        m1, m2, m3 = 10, 8, 4

        container = ttk.Frame(frame)
        container.grid(row=1, column=0, sticky="nsew", padx=6, pady=(6, 6))
        container.grid_columnconfigure(0, weight=1)

        style = ttk.Style(container)

        style1 = f"TaxiPB.{uuid.uuid4().hex}.Horizontal.TProgressbar"
        style2 = f"BusPB.{uuid.uuid4().hex}.Horizontal.TProgressbar"
        style3 = f"TubePB.{uuid.uuid4().hex}.Horizontal.TProgressbar"

        for sname, col in [(style1, c1), (style2, c2), (style3, c3)]:
            style.configure(
                sname,
                thickness=bar_thickness,
                troughcolor=trough_color,
                background=col,
                bordercolor=trough_color,
                lightcolor=col,
                darkcolor=col,
            )

        p1 = StagedProgressBar.StagedProgress(
            container, title=t1, stages=m1, length=length,
            bar_color=c1, trough_color=trough_color, style=style1
        )
        p2 = StagedProgressBar.StagedProgress(
            container, title=t2, stages=m2, length=length,
            bar_color=c2, trough_color=trough_color, style=style2
        )
        p3 = StagedProgressBar.StagedProgress(
            container, title=t3, stages=m3, length=length,
            bar_color=c3, trough_color=trough_color, style=style3
        )

        # IMPORTANT: expand=True so they stretch with the container
        p1.pack(fill="x", expand=True, pady=(0, row_padding))
        p2.pack(fill="x", expand=True, pady=(0, row_padding))
        p3.pack(fill="x", expand=True)

        p1.set_stage(m1)
        p2.set_stage(m2)
        p3.set_stage(m3)

        while len(self.player_widgets) <= index:
            self.player_widgets.append({})

        self.player_widgets[index]["ticket_bars"] = {"taxi": p1, "bus": p2, "tube": p3}
        self.player_widgets[index]["ticket_max"] = {"taxi": m1, "bus": m2, "tube": m3}
        return self.player_widgets[index]["ticket_bars"]

    def create_mister_x_info_panel(self, frame, index):
        """Display available move tickets for Mr X (Taxi/Bus/Tube/Black/X2)."""

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        name_label = tk.Label(
            frame,
            text=self.players[index][0],
            font=("Arial", 11, "bold"),
            bg=self.colours[index],
            fg="white"
        )
        name_label.grid(row=0, column=0, sticky="ew", padx=(10, 10), pady=(8, 0))

        length = 150
        trough_color = "#E6E6E6"
        row_padding = 6
        bar_thickness = 6

        t1, t2, t3, t4, t5 = "Taxi", "Bus", "Tube", "Black ticket", "X2"
        c1, c2, c3, c4, c5 = "yellow", "green", "red", "black", "orange"

        m1, m2, m3 = 4, 3, 3
        m4 = len(self.controller.players)
        m5 = 2

        container = ttk.Frame(frame)
        container.grid(row=1, column=0, sticky="nsew", padx=6, pady=(6, 6))
        container.grid_columnconfigure(0, weight=1)

        style = ttk.Style(container)

        style1 = f"MrXTaxiPB.{uuid.uuid4().hex}.Horizontal.TProgressbar"
        style2 = f"MrXBusPB.{uuid.uuid4().hex}.Horizontal.TProgressbar"
        style3 = f"MrXTubePB.{uuid.uuid4().hex}.Horizontal.TProgressbar"
        style4 = f"MrXBlackPB.{uuid.uuid4().hex}.Horizontal.TProgressbar"
        style5 = f"MrXX2PB.{uuid.uuid4().hex}.Horizontal.TProgressbar"

        for sname, col in [(style1, c1), (style2, c2), (style3, c3), (style4, c4), (style5, c5)]:
            style.configure(
                sname,
                thickness=bar_thickness,
                troughcolor=trough_color,
                background=col,
                bordercolor=trough_color,
                lightcolor=col,
                darkcolor=col,
            )

        p1 = StagedProgressBar.StagedProgress(container, title=t1, stages=m1, length=length,
                                              bar_color=c1, trough_color=trough_color, style=style1)
        p2 = StagedProgressBar.StagedProgress(container, title=t2, stages=m2, length=length,
                                              bar_color=c2, trough_color=trough_color, style=style2)
        p3 = StagedProgressBar.StagedProgress(container, title=t3, stages=m3, length=length,
                                              bar_color=c3, trough_color=trough_color, style=style3)
        p4 = StagedProgressBar.StagedProgress(container, title=t4, stages=m4, length=length,
                                              bar_color=c4, trough_color=trough_color, style=style4)
        p5 = StagedProgressBar.StagedProgress(container, title=t5, stages=m5, length=length,
                                              bar_color=c5, trough_color=trough_color, style=style5)

        p1.pack(fill="x", expand=True, pady=(0, row_padding))
        p2.pack(fill="x", expand=True, pady=(0, row_padding))
        p3.pack(fill="x", expand=True, pady=(0, row_padding))
        p4.pack(fill="x", expand=True, pady=(0, row_padding))
        p5.pack(fill="x", expand=True)

        p1.set_stage(m1)
        p2.set_stage(m2)
        p3.set_stage(m3)
        p4.set_stage(m4)
        p5.set_stage(m5)

        while len(self.player_widgets) <= index:
            self.player_widgets.append({})

        self.player_widgets[index]["ticket_bars"] = {
            "taxi": p1,
            "bus": p2,
            "tube": p3,
            "black": p4,
            "x2": p5,
        }
        self.player_widgets[index]["ticket_max"] = {
            "taxi": m1, "bus": m2, "tube": m3, "black": m4, "x2": m5
        }
        return self.player_widgets[index]["ticket_bars"]

    
    
    def create_player_panel(self, frame, index):
        """Create a panel for an existing player"""
        # Top: Player name
        name_label = tk.Label(frame, text=self.players[index][0],
                             font=('Arial', 11, 'bold'),
                             bg=self.colours[index],
                             fg='white')
        name_label.grid(row=0, column=0, sticky="w",padx= (10,0), pady=(8, 0))
        


        # Middle: Starting location
        info_frame = tk.Frame(frame, bg="white")
        info_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        info_label = tk.Label(info_frame, text="Starting pos",
                             font=('Arial', 7, 'bold'),
                             bg="white",
                             fg='black')
        info_label.grid(row=0, column=0, sticky="nw",padx= (2,0), pady=(2, 0))

        var = self.starting_strings[index]  # must be a tk.StringVar (or IntVar, etc.)

        # Remove an existing trace for this index (prevents double-calling after UI rebuild)
        if not hasattr(self, "_pos_trace_ids"):
            self._pos_trace_ids = {}

        old_id = self._pos_trace_ids.get(index)
        if old_id:
            try:
                var.trace_remove("write", old_id)
            except tk.TclError:
                pass  # trace might already be gone

        # Add new trace; use lambda to bind the player index
        trace_id = var.trace_add("write", lambda *_args, i=index: self.on_position_change(i))
        self._pos_trace_ids[index] = trace_id
        # Create entry widget
        name_entry = tk.Entry(info_frame, 
                             textvariable=self.starting_strings[index], 
                             font=('calibre', 10, 'normal'),
                             state='disabled',  # Start disabled for RNG
                             width=8)
        name_entry.grid(row=0, column=1, sticky="w", padx=(5, 0), pady=(2, 0))
        
        # Create radio variable for this player
        if index not in self.radio_vars:
            # Check if player has RNG value
            current_val = self.starting_strings[index].get()
            if current_val == "RNG":
                self.radio_vars[index] = tk.IntVar(value=1)  # Random
            else:
                self.radio_vars[index] = tk.IntVar(value=2)  # Manual
        else:
            # Keep existing value
            pass
        
        # Radio buttons with correct callback
        radio_frame = tk.Frame(info_frame)
        radio_frame.grid(row=1, column=0, columnspan=2, sticky="w", pady=(5, 0))
        
        # Random radio button
        radio_1 = tk.Radiobutton(
            radio_frame, 
            text="Random", 
            variable=self.radio_vars[index], 
            value=1,
            command=lambda idx=index, entry=name_entry: self.__on_radial_selection(idx, entry)
        )
        radio_1.pack(side=tk.LEFT, padx=(2, 5))
        
        # Manual radio button
        radio_2 = tk.Radiobutton(
            radio_frame, 
            text="Manual", 
            variable=self.radio_vars[index], 
            value=2,
            command=lambda idx=index, entry=name_entry: self.__on_radial_selection(idx, entry)
        )
        radio_2.pack(side=tk.LEFT)



        # Bottom: Action combobox
        if index == 0:  # Player 1 has special options
            options = ["Manual X", "X Type1", "X Type2"]
        else:
            options = ["Manual", "Type 1", "Type 2"]
        
        combobox = ttk.Combobox(frame,
                               values=options,
                               state="readonly",
                               font=('Arial', 9))
        combobox.set(options[0])
        combobox.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 8))
        
        # Bind events
        combobox.player_index = index
        combobox.bind("<<ComboboxSelected>>", 
                     lambda e, idx=index: self.on_agent_selection(idx))
        
        # Add remove button for players (except first 2 if you want)
        if index == (len(self.players) - 1) and index > 2:  # Can remove players added after initial 2
            remove_btn = tk.Button(frame,
                              text="X",
                              font=('Arial', 10, 'bold'),
                              bg="#FF6B6B",
                              fg="white",
                              activebackground="#FF3333",
                              activeforeground="white",
                              relief=tk.FLAT,
                              borderwidth=0,
                              padx=0,
                              pady=0,
                              width=2,
                              height=1,
                              command=lambda idx=index: self.delete_player())
            remove_btn.grid(row=0, column=1, sticky="e", padx=(0, 10), pady=(8, 0))
    
    def create_add_player_button(self, frame, index):
        """Create the 'Add Player' button in the next available spot"""
        
        # Make the frame look clickable
        frame.config(bg="#F0F0F0", relief=tk.GROOVE)
        
        # Center the add button
        button = tk.Button(frame,
                          text="+ ADD PLAYER",
                          font=('Arial', 12, 'bold'),
                          bg="#4CAF50",
                          fg="white",
                          relief=tk.RAISED,
                          command=self.add_player)
        button.place(relx=0.5, rely=0.5, anchor="center", 
                    relwidth=0.8, relheight=0.6)
        
        # Optional: Add help text
        help_label = tk.Label(frame,
                             text=f"Player {index + 1}",
                             font=('Arial', 9, 'italic'),
                             bg="#F0F0F0",
                             fg="#666666")
        help_label.place(relx=0.5, rely=0.9, anchor="center")
    
    def create_blank_frame(self, frame, index):
        """Create a blank/inactive frame for future players"""
        frame.config(bg="#F8F8F8", relief=tk.FLAT)
        
        # Grayed out placeholder
        placeholder = tk.Label(frame,
                              text=f"Player {index + 1}\n(Empty)",
                              font=('Arial', 10),
                              bg="#F8F8F8",
                              fg="#CCCCCC")
        placeholder.place(relx=0.5, rely=0.5, anchor="center")


    
    def add_player(self):
        self.controller.add_player()
        number_of_players = len(self.controller.players)
        if number_of_players < 7: 
                self.starting_strings.append(tk.StringVar(value="RNG"))
        self.create_panels()
        self.map_obj.draw_full_state(self.controller.state)


    def delete_player(self):
        self.controller.delete_player()
        number_of_players = len(self.players)
        if number_of_players > 3:
            # Remove the radio variable too
            removed_index = len(self.players)
            if removed_index in self.radio_vars:
                del self.radio_vars[removed_index]
            if removed_index in self.starting_strings:
                del self.starting_strings[removed_index]
        self.create_panels()
        self.map_obj.draw_full_state(self.controller.state)


    def on_agent_selection(self, idx):
        print(f"Selected combo {idx}")

                
    def highlight_panel(self, panel_index, highlight=True, color="lightblue"):
        """Highlight panel by changing background color"""
        if 0 <= panel_index < len(self.subframes):
            frame = self.subframes[panel_index]
            
            if highlight:
                # Store original color before changing
                if not hasattr(frame, '_original_bg'):
                    frame._original_bg = frame.cget('bg')
                
                # Change background color
                frame.configure(bg=color)
                
                # Also highlight child widgets
                for widget in frame.winfo_children():
                    if isinstance(widget, tk.Frame):
                        widget.configure(bg=color)
            else:
                # Restore original color
                if hasattr(frame, '_original_bg'):
                    frame.configure(bg=frame._original_bg)
                    
                    # Restore child frames
                    for widget in frame.winfo_children():
                        if isinstance(widget, tk.Frame):
                            widget.configure(bg=frame._original_bg)

    def on_position_change(self, player_index: int, *_):
        """
        Called whenever the StringVar for this player's position changes.
        `*_` absorbs the (name, index, mode) arguments Tkinter passes.
        """
        new_value = self.starting_strings[player_index].get()
        success = self.controller.set_player_pos(player_index, new_value)
        if success:
            self.map_obj.draw_full_state(self.controller.state)



    def __on_radial_selection(self, player_index, entry):
        """Handle radio button selection for a specific player"""
        # Get the radio variable for this player
        radio_var = self.radio_vars.get(player_index)
        
        if radio_var is None:
            return
        
        # Get the current value from the radio variable
        selection = radio_var.get()
        
        if selection == 1:  # Random
            entry.config(state='disabled')
            # Update the StringVar to "RNG"
            self.starting_strings[player_index].set("RNG")
            print(f"Player {player_index}: Random selected - entry disabled")
        elif selection == 2:  # Manual
            entry.config(state='normal')
            # If entry is empty or has RNG, set a default value
            current_text = entry.get()
            if not current_text or current_text == "RNG":
                random_num = self.controller.random_locs[player_index]
                entry.delete(0, tk.END)
                entry.insert(0, f"{random_num}")  # Default position
            print(f"Player {player_index}: Manual selected - entry enabled")

    def update_tickets(self, state):
        tickets = state.player_cards
        for player_index in range(0, len(self.players)):
            bars = self.player_widgets[player_index]["ticket_bars"]
            bars["taxi"].set_stage(tickets[player_index]["taxi"])
            bars["bus"].set_stage(tickets[player_index]["bus"])
            bars["tube"].set_stage(tickets[player_index]["tube"])
            if player_index == 0:
                bars["black"].set_stage(tickets[player_index]["black"])
                bars["x2"].set_stage(tickets[player_index]["x2"])



if __name__ == "__main__":
    game = GameUI("1335x1000")