import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
import threading
import requests
import os
import time
from flask import Flask, send_file, request, abort, render_template, make_response, session, redirect, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = "Felix.com"

lock = threading.Lock()

class Window(tk.Tk):
    def create_navigation_bar(self):
        navigation_frame = ttk.Frame(self)
        navigation_frame.pack(side=tk.LEFT, fill=tk.Y)

        buttons = [
            ("Team", self.show_Team_frame),
            ("Players", self.show_player_frame),
            ("SPIEL", self.show_SPIEL_frame),
            #("Contact", self.show_contact_frame),
        ]

        button_width = 10  # Set a fixed width for all buttons

        for text, command in buttons:
            button = ttk.Button(navigation_frame, text=text, command=command, width=button_width)
            button.pack(side=tk.TOP, anchor=tk.W, pady=5)
            
            
    def __init__(self, start_server=True):
        super().__init__()
        self.name_entries = []
        self.label_list = []
        self.updated_data = {}
        self.variable_dict = {}
        self.team_button_list = []
        self.spiel_buttons = {}
        self.teams_playing = [None, None]

        # Set window title
        self.title("Football Tournament Manager")
        self.state('zoomed')
        try:
            icon_path = os.path.join('..', 'icon.ico')
            self.iconbitmap(icon_path)
        except:
            icon_path = os.path.join('icon.ico')
            self.iconbitmap(icon_path)
        
        self.init_sqlite_db()
        
        #menu = tk.Menu(self)
        #self.config(menu=menu)
        #filemenu = tk.Menu(menu)
        #menu.add_cascade(label="Manager", menu=filemenu)
        #filemenu.add_command(label="Exit", command=self.quit)

        # Create and pack the navigation bar
        self.create_navigation_bar()

        # Create frames for different sets of elements
        self.Team_frame = ttk.Frame(self)
        self.player_frame = ttk.Frame(self)
        self.SPIEL_frame = ttk.Frame(self)
        #self.contact_frame = ttk.Frame(self, bg="lightyellow")

        # Create elements for each frame
        self.create_Team_elements()
        self.create_player_elements()
        self.create_SPIEL_elements()
        #self.create_contact_elements()

        # Display the default frame
        self.show_frame(self.Team_frame)
        
        print("finished init")
        
        
        if start_server:
            server_thread = threading.Thread(target=self.start_server)
            server_thread.start()
    
        
    def start_server(self):
        app.run(debug=False, threaded=True, port=5000, host="0.0.0.0", use_reloader=False)
    
    
    def init_sqlite_db(self):
        self.db_path = "data/data.db"
        
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        
        teamDataTableCreationQuery = """
        CREATE TABLE IF NOT EXISTS teamData (
            id INTEGER PRIMARY KEY,
            teamName TEXT UNIQUE,
            goals INTEGER DEFAULT 0,
            goalsReceived INTEGER DEFAULT 0,
            games INTEGER DEFAULT 0,
            points INTEGER DEFAULT 0,
            groupNumber INTEGER
        )
        """
        self.cursor.execute(teamDataTableCreationQuery)
        self.connection.commit()
        
        playerDataTableCreationQuery = """
        CREATE TABLE IF NOT EXISTS playerData (
            id INTEGER PRIMARY KEY,
            playerName TEXT UNIQUE,
            playerNumber INTEGER,
            teamId INTEGER REFERENCES teamData(id) DEFAULT 0,
            goals INTEGER DEFAULT 0
        )
        """
        self.cursor.execute(playerDataTableCreationQuery)
        self.connection.commit()
        
        matchDataTableCreationQuery = """
        CREATE TABLE IF NOT EXISTS matchData (
            id INTEGER PRIMARY KEY,
            groupNumber INTEGER,
            team1Id INTEGER,
            team2Id INTEGER,
            team1Goals INTEGER DEFAULT 0,
            team2Goals INTEGER DEFAULT 0,
            matchTime TEXT
        )
        """
        self.cursor.execute(matchDataTableCreationQuery)
        self.connection.commit()
        
        
        
            
            
##############################################################################################
    def add_name_entry(self, entry_text=""):
        count = len(self.name_entries) + 1

        # Create a label with "Team 1" and the count
        label_text = f'Team {count}'
        label = ttk.Label(self.frame, text=label_text, font=("Helvetica", 14))  # Increase font size
        label.grid(row=len(self.name_entries), column=0, padx=5, pady=5, sticky='e')

        # Create a new entry field
        new_entry = ttk.Entry(self.frame, font=("Helvetica", 14))  # Increase font size
        
        # Write entry_text to the entry field if it is not empty
        if entry_text:
            new_entry.insert(0, entry_text)

        new_entry.grid(row=len(self.name_entries), column=1, pady=5, sticky='we')
        self.name_entries.append(new_entry)
        self.label_list.append(label)

    def on_frame_configure(self, canvas):
        canvas.configure(scrollregion=canvas.bbox("all"))
        
    def reload_button_command(self):
        # Delete all entry fields
        for entry in self.name_entries:
            entry.destroy()
        self.name_entries = []
        
        for label in self.label_list:
            label.destroy()
        
        # Read the names from the file and put them into the entry fields
        self.write_names_into_entry_fields()
        
    def save_team_names_in_db(self):
        
        
        name_entries = self.name_entries
        #print(name_entries)

        # Get existing teams from the database
        self.cursor.execute("SELECT teamName FROM teamData")
        existing_teams = {row[0] for row in self.cursor.fetchall()}

        # Update existing teams and add new teams with default values
        for entry in name_entries:
            team_name = entry.get().strip()
            #print(team_name)
            if team_name != "":
                # Update existing team
                if not team_name in existing_teams:
                    # Add new team with default values
                    self.cursor.execute("INSERT INTO teamData (teamName, goals) VALUES (?, 0)", (team_name,))
                    existing_teams.add(team_name)

        # Delete teams not in the entries
        teams_to_delete = existing_teams - {entry.get().strip() for entry in name_entries}
        for team_name in teams_to_delete:
            self.cursor.execute("DELETE FROM teamData WHERE teamName = ?", (team_name,))

        #print("tests")
        self.updated_data.update({"Team": self.read_teamNames().pop(0)})
        self.connection.commit()
        
    
    def write_names_into_entry_fields(self):
        selectTeams = """
        SELECT teamName FROM teamData
        ORDER BY id ASC
        """
        self.cursor.execute(selectTeams)
        
        for teamName in self.cursor.fetchall():
            self.add_name_entry(teamName[0])
            

    def create_Team_elements(self):
        
        # Create elements for the Team frame
        canvas = tk.Canvas(self.Team_frame)
        canvas.pack(side="left", fill="both", expand=True)
        
        # Create a scrollbar and connect it to the canvas
        scrollbar = ttk.Scrollbar(self.Team_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self.frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=self.frame, anchor="nw")
        
        name_entries = []
        self.write_names_into_entry_fields()

        self.frame.bind("<Configure>", lambda event, canvas=canvas: self.on_frame_configure(canvas))

        # Button to add a new name entry
        add_button = ttk.Button(self.Team_frame, text="Add Name", command=self.add_name_entry)
        add_button.pack(pady=10)

        # Button to retrieve the entered names


        submit_button = ttk.Button(self.Team_frame, text="Submit", command=self.save_team_names_in_db)
        submit_button.pack(pady=10)

        
        reload_button = ttk.Button(self.Team_frame, text="Reload", command=self.reload_button_command)
        reload_button.pack(pady=10)
        

##############################################################################################

##############################################################################################

    def create_player_elements(self):
        # Create elements for the player frame
        #player_button = tk.Button(self.player_frame, text="player Button", command=self.player_button_command)
        #player_button.pack(pady=10)
        # Create elements for the Team frame
        canvas = tk.Canvas(self.player_frame)
        canvas.pack(fill="both", expand=True, side="bottom")

        # Create a scrollbar and connect it to the canvas
        scrollbar = ttk.Scrollbar(self.player_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.LEFT, fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        self.frameplayer = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=self.frameplayer, anchor="nw")
        
        
        # Button to add a new name entry
        add_button = ttk.Button(self.player_frame, text="Add Name", command=lambda: self.add_name_entry_player(self.frameplayer, "Player"))
        add_button.pack(pady=5, padx=5, anchor=tk.NE, side=tk.RIGHT)    

        # Button to retrieve the entered names


        submit_button = ttk.Button(self.player_frame, text="Submit", command=self.save_names_player)
        submit_button.pack(pady=5, padx=5, anchor=tk.NE, side=tk.RIGHT)    

        
        reload_button = ttk.Button(self.player_frame, text="Reload", command=self.reload_button_player_command)
        reload_button.pack(pady=5, padx=5, anchor=tk.NE, side=tk.RIGHT)    
        
        self.selected_team = ""
        self.team_button_list = []
        
        team_IDs = self.read_teamIds()
        teamNames = self.read_teamNames()
        #print(teamNames)
        
        for i, teamID in enumerate(team_IDs):
            teamName = teamNames[int(teamID)]
            #print(teamName)
            team_button = ttk.Button(
                self.player_frame,
                text=teamName,
                command=lambda id=teamID, i2=i: self.select_team(id, self.team_button_list, i2)
            )
            team_button.pack(pady=5, padx=5, anchor=tk.NW, side=tk.LEFT)
            self.team_button_list.append(team_button)
            
        
        
    def save_names_player(self, team_id=-1):
        entries = self.variable_dict.get(f"entries{self.frameplayer}")
        entries2 = self.variable_dict.get(f"entries2{self.frameplayer}")
        entries3 = self.variable_dict.get(f"entries3{self.frameplayer}")

        if team_id == -1:
            team_id = self.selected_team

        if entries:
            
            

            # Get existing players for the team from the database
            self.cursor.execute("SELECT playerName FROM playerData WHERE teamId = ?", (team_id,))
            existing_players = {row[0] for row in self.cursor.fetchall()}

            # Iterate through the current entries and update or insert as needed
            for entry, entrie2, entrie3 in zip(entries, entries2, entries3):
                #print(entries)
                entry_text = str(entry.get())
                entry_text2 = str(entrie2.get())
                entry_text3 = str(entrie3.get())

                if entry_text:
                    # Update existing player
                    if entry_text in existing_players:
                        update_query = "UPDATE playerData SET playerNumber = ?, goals = ? WHERE playerName = ? AND teamId = ?"
                        self.cursor.execute(update_query, (entry_text2, entry_text3, entry_text, team_id))
                    else:
                        # Add new player
                        try:
                            insert_query = "INSERT INTO playerData (playerName, playerNumber, goals, teamId) VALUES (?, ?, ?, ?)"
                            self.cursor.execute(insert_query, (entry_text, entry_text2, entry_text3, team_id))
                        except sqlite3.IntegrityError:
                            
                            for i in range(1, 100):
                                if f"{entry_text} {i}" not in existing_players:
                                    entry_text = f"{entry_text} {i}"
                                    break
                            insert_query = "INSERT INTO playerData (playerName, playerNumber, goals, teamId) VALUES (?, ?, ?, ?)"
                            self.cursor.execute(insert_query, (entry_text, entry_text2, entry_text3, team_id))
                                

            # Delete players not in the entries
            players_to_delete = existing_players - {entry.get() for entry in entries}
            for player_name in players_to_delete:
                self.cursor.execute("DELETE FROM playerData WHERE playerName = ? AND teamId = ?", (player_name, team_id))

            self.connection.commit()
            
            

        ###self.updated_data.update({"Players": {self.selected_team: self.read_team_names_player(self.selected_team)}})
            
    
    def add_name_entry_player(self, Frame, Counter, entry_text="", entry_text2="", entry_text3=""):
        varcountname = f"count{Frame}"
        varentrie1name = f"entries{Frame}"
        varentrie2name = f"entries2{Frame}"
        varentrie3name = f"entries3{Frame}"
        varlabelname = f"label{Frame}"

        # Check if the variable already exists in the dictionary
        if varcountname not in self.variable_dict:
            self.variable_dict[varcountname] = 0  # Initialize count to 0

        if varentrie1name not in self.variable_dict:
            self.variable_dict[varentrie1name] = []
            
        if varentrie2name not in self.variable_dict:
            self.variable_dict[varentrie2name] = []

        if varentrie3name not in self.variable_dict:
            self.variable_dict[varentrie3name] = []
        
        if varlabelname not in self.variable_dict:
            self.variable_dict[varlabelname] = []

        # Now you can access the count using the dynamic variable name
        count = self.variable_dict[varcountname] + 1

        # Update the count in the dictionary
        self.variable_dict[varcountname] = count

        # Create a label with "Team 1" and the count
        label_text = f'{Counter} {count}'
        label = ttk.Label(Frame, text=label_text, font=("Helvetica", 14))  # Increase font size
        label.grid(row=len(self.variable_dict[varentrie1name]), column=0, padx=5, pady=5, sticky='e')

        # Create a new entry field
        new_entry = ttk.Entry(Frame)  # Increase font size
        
        new_entry2 = ttk.Entry(Frame)  # Increase font size
        
        new_entry3 = ttk.Entry(Frame)  # Increase font size
        #print("entry_text", entry_text)
        #print("new_entry")

        # Write entry_text to the entry field if it is not empty
        if entry_text:
            new_entry.insert(0, entry_text)
            
        if entry_text2:
            new_entry2.insert(0, entry_text2)
            
        if entry_text3:
            new_entry3.insert(0, entry_text3)
        else:
            new_entry3.insert(0, "0")
        
        

        new_entry.grid(row=len(self.variable_dict[varentrie1name]), column=1, pady=5, sticky='we')
        new_entry2.grid(row=len(self.variable_dict[varentrie1name]), column=2, pady=5, sticky='we')
        new_entry3.grid(row=len(self.variable_dict[varentrie1name]), column=3, pady=5, sticky='we')
        self.variable_dict[varentrie1name].append(new_entry)
        self.variable_dict[varentrie2name].append(new_entry2)
        self.variable_dict[varentrie3name].append(new_entry3)
        self.variable_dict[varlabelname].append(label)

    
    def write_names_into_entry_fields_players(self, teamID, Counter, Frame):
        # Read player names using read_player_stats function
        output = self.read_player_stats(teamID, True)
        player_names = [row[0] for row in output]
        player_numbers = [row[1] for row in output]
        goals = [row[2] for row in output]

        # if the file is empty or no names are read, add an empty entry
        if not player_names:
            self.add_name_entry_player(Frame, Counter)
        else:
            # if names are read, put them into the entry fields
            for player_name, player_number, goal in zip(player_names, player_numbers, goals):
                self.add_name_entry_player(Frame, Counter, player_name, player_number, goal)


    def reload_button_player_command(self):
        
        for button in self.team_button_list:
            button.destroy()
        
        self.selected_team = ""
        self.team_button_list = []
        
        team_IDs = self.read_teamIds()
        teamNames = self.read_teamNames()
        
        for i, teamID in enumerate(team_IDs):
            teamName = teamNames[int(teamID)]
            team_button = ttk.Button(
                self.player_frame,
                text=teamName,
                command=lambda id=teamID, i2=i: self.select_team(id, self.team_button_list, i2)
            )
            team_button.pack(pady=5, padx=5, anchor=tk.NW, side=tk.LEFT)
            self.team_button_list.append(team_button)
    
        
        varcountname = f"count{str(self.frameplayer)}"
        varentrie1name = f"entries{str(self.frameplayer)}"
        varentrie2name = f"entries2{str(self.frameplayer)}"
        varentrie3name = f"entries3{str(self.frameplayer)}"
        varlabelname = f"label{str(self.frameplayer)}"

        # Check if the key exists in the dictionary
        if self.variable_dict.get(varentrie1name):
            # Access the value associated with the key
            if self.variable_dict[varentrie1name] != []:
                for entry in self.variable_dict[varentrie1name]:
                    entry.destroy()

                for label in self.variable_dict[varlabelname]:
                    label.destroy()
                
                for entry in self.variable_dict[varentrie2name]:
                    entry.destroy()
                    
                for entry in self.variable_dict[varentrie3name]:
                    entry.destroy()
    
        
        
        self.variable_dict[varcountname] = 0
    
    
    def select_team(self, teamID, team_button_list, index):
        
        #for button in team_button_list:
        #    button.config(bg="lightgray")
        
        team_button = team_button_list[index]
        
        varcountname = f"count{str(self.frameplayer)}"
        varentrie1name = f"entries{str(self.frameplayer)}"
        varentrie2name = f"entries2{str(self.frameplayer)}"
        varentrie3name = f"entries3{str(self.frameplayer)}"
        varlabelname = f"label{str(self.frameplayer)}"

        # Check if the key exists in the dictionary
        if self.variable_dict.get(varentrie1name):
            # Access the value associated with the key
            if self.variable_dict[varentrie1name] != []:
                for entry in self.variable_dict[varentrie1name]:
                    entry.destroy()

                for label in self.variable_dict[varlabelname]:
                    label.destroy()
                
                for entry in self.variable_dict[varentrie2name]:
                    entry.destroy()
                
                for entry in self.variable_dict[varentrie3name]:
                    entry.destroy()
        
        self.selected_team = teamID
        
        self.variable_dict[varcountname] = 0
        self.variable_dict[varentrie1name] = []
        self.variable_dict[varentrie2name] = []
        self.variable_dict[varentrie3name] = []
        self.variable_dict[varlabelname] = []
        
        
        self.write_names_into_entry_fields_players(teamID, "Player", self.frameplayer)
          
            
    def read_player_stats(self, teamID, readGoals=False, playerID=-1):
        output = []

        if readGoals and playerID == -1:
            getData = """
            SELECT playerName, playerNumber, goals FROM playerData
            WHERE teamId = ?
            ORDER BY id ASC
            """
            self.cursor.execute(getData, (teamID,))

            for row in self.cursor.fetchall():
                output.append(row)

        elif readGoals and playerID != -1:
            print("readGoals", readGoals, "playerID", playerID, "teamID", teamID)
            getData = """
            SELECT playerName, playerNumber, goals FROM playerData
            WHERE teamId = ? AND id = ?
            ORDER BY id ASC
            """
            self.cursor.execute(getData, (teamID, playerID))

            for row in self.cursor.fetchall():
                output.append(row)
                
        elif not readGoals and playerID != -1:
            getData = """
            SELECT playerName, playerNumber FROM playerData
            WHERE teamId = ? AND id = ?
            ORDER BY id ASC
            """
            self.cursor.execute(getData, (teamID, playerID))
            
            for row in self.cursor.fetchall():
                output.append(row)
            
        else:
            getData = """
            SELECT playerName, playerNumber FROM playerData
            WHERE teamId = ?
            ORDER BY id ASC
            """
            self.cursor.execute(getData, (teamID,))
            
            for row in self.cursor.fetchall():
                output.append(row)
                

        return output
            
            
    def read_teamNames(self, teams_to_read=-1):
        teamNames = [""]
        
        if teams_to_read != -1:
            for team in teams_to_read:
                if team != None:
                    team = int(team) + 1
                        
                    selectTeam = """
                    SELECT teamName FROM teamData
                    WHERE id = ?
                    ORDER BY id ASC
                    """
                    self.cursor.execute(selectTeam, (team,))
                    result = self.cursor.fetchone()
                    if result is not None:
                        #print(result)
                        teamNames.append(result[0])
          
        else:
            selectTeams = """
            SELECT teamName FROM teamData
            ORDER BY id ASC
            """
            self.cursor.execute(selectTeams)
        
            for team in self.cursor.fetchall():
                teamNames.append(team[0])
                
        return teamNames
    
    
    def read_teamIds(self):
        teamIds = []
        
        self.cursor.execute("SELECT id FROM teamData")
        
        for id in self.cursor.fetchall():
            teamIds.append(id[0])

        return teamIds


    def get_team_id_from_team_name(self, team_name):

        self.cursor.execute("SELECT id FROM teamData WHERE teamName = ?", (team_name,))
        
        team_id = self.cursor.fetchone()[0]
        
        return team_id
    
    def get_player_id_from_player_name(self, player_name):
        
        self.cursor.execute("SELECT id FROM playerData WHERE playerName = ?", (player_name,))
        
        player_id = self.cursor.fetchone()[0]
        
        return player_id


##############################################################################################
##############################################################################################
##############################################################################################

    def create_SPIEL_elements(self):
        # Create elements for the SPIEL frame
        
        manual_frame = ttk.Frame(self.SPIEL_frame)
        manual_frame.pack(pady=5, anchor=tk.S, side=tk.BOTTOM, padx=5, fill=tk.X)
        
        manual_manual_frame = ttk.Frame(manual_frame)
        manual_manual_frame.pack(pady=0, anchor=tk.SE, side=tk.RIGHT, padx=0)
        
        SPIEL_button = ttk.Button(manual_manual_frame, text="Reload", command=lambda : self.reload_button_command_common(self.SPIEL_frame, self.create_SPIEL_elements))
        SPIEL_button.pack(pady=10, side=tk.BOTTOM, anchor=tk.S) 
        
        
        # Assuming self.spiel_buttons is initialized as an empty dictionary
        self.spiel_buttons = {}

        #print("self.teams_playing", self.teams_playing)
        
        for i, _ in enumerate(self.teams_playing):
            
            #print(self.teams_playing)
            
            team_names = self.read_teamNames()
            if self.teams_playing[i] is not None:
                #print("i" , i, "teamnames", team_names)
                #print(self.teams_playing[i])
                team_name = team_names[self.teams_playing[i]]
                
            else:
                # Handle the case when self.teams_playing[i + 1] is None
                # For example, you can set team_name to an empty string
                break
                
            team_id = self.teams_playing[i]

            #print(team)
            
            # Initialize the dictionary for the current team
            self.spiel_buttons[team_id] = {}

                    
            self.for_team_frame = ttk.Frame(self.SPIEL_frame)
            self.for_team_frame.pack(pady=10, anchor=tk.NW, side=tk.TOP, fill="both", padx=10, expand=True)
            
            # Create global scores buttons, one for up and one for down
            score_button_frame = ttk.Frame(self.for_team_frame)
            score_button_frame.pack(pady=10, anchor=tk.E, side=tk.RIGHT, padx=10)
            
            score_button_up = ttk.Button(score_button_frame, text="UP", command=lambda team=team_id: self.global_scored_a_point(team, "UP"))
            score_button_up.pack(pady=2, anchor=tk.N, side=tk.TOP, expand=True, fill=tk.X)
            
            score_label = ttk.Label(score_button_frame, text="45", font=("Helvetica", 14))
            score_label.pack(pady=2, anchor=tk.N, side=tk.TOP, expand=True, fill=tk.X)
            
            score_button_down = ttk.Button(score_button_frame, text="DOWN", command=lambda team=team_id: self.global_scored_a_point(team, "DOWN"))
            score_button_down.pack(pady=2, anchor=tk.N, side=tk.BOTTOM, expand=True, fill=tk.X)
            
            self.team_label = ttk.Label(self.for_team_frame, text=team_name, font=("Helvetica", 14))
            self.team_label.pack(side=tk.LEFT, pady=2, anchor=tk.NW)
            
            self.spiel_buttons[team_id]["global"] = (self.for_team_frame, self.team_label)
            
            frame_frame = ttk.Frame(self.for_team_frame)
            frame_frame.pack(side=tk.TOP, pady=0, anchor=tk.N)

            up_frame = ttk.Frame(frame_frame)
            up_frame.pack(side=tk.TOP, padx=0, pady=0, anchor=tk.NW)

            down_frame = ttk.Frame(frame_frame)
            down_frame.pack(side=tk.TOP, padx=0, pady=0, anchor=tk.SW)
            

            for i, (player_name, player_number, goals) in enumerate(self.read_player_stats(team_id, True)):       
                #print(type(player_name), player_name)
                player_index = i 
                player_id = self.get_player_id_from_player_name(player_name)
                if i < 8:
                    self.group_frame = ttk.Frame(up_frame)
                    self.group_frame.pack(side=tk.LEFT, padx=10, pady=10, anchor=tk.N)
                else:
                    self.group_frame = ttk.Frame(down_frame)
                    self.group_frame.pack(side=tk.LEFT, padx=10, pady=10, anchor=tk.S)
                
                #self.group_frame = tk.Frame(self.for_team_frame, background="lightcoral")
                #self.group_frame.pack(side=tk.LEFT, padx=10, pady=10)

                playertext1 = ttk.Label(self.group_frame, text=f"Player {i}", font=("Helvetica", 14))
                playertext1.pack(side=tk.TOP, pady=2, expand=True, fill=tk.X)
                
                playertext2_text = f"{player_name} - {player_number}"
                
                playertext2 = ttk.Label(master=self.group_frame, text=playertext2_text , font=("Helvetica", 14))
                playertext2.pack(side=tk.TOP, pady=2, expand=True, fill=tk.X)
                
                playertext3 = ttk.Label(self.group_frame, text=f"Tore {str(goals)}", font=("Helvetica", 14))
                playertext3.pack(side=tk.TOP, pady=2, expand=True, fill=tk.X)

                playerbutton1 = ttk.Button(self.group_frame, text="UP", command=lambda team=team_id, player_id1=player_id, player_index = player_index: self.player_scored_a_point(team, player_id1, player_index,  "UP"))
                playerbutton1.pack(side=tk.TOP, pady=2, expand=True, fill=tk.X)
                
                playerbutton2 = ttk.Button(self.group_frame, text="DOWN", command=lambda team=team_id, player_id1=player_id, player_index = player_index: self.player_scored_a_point(team, player_id1, player_index, "DOWN"))
                playerbutton2.pack(side=tk.TOP, pady=2, expand=True, fill=tk.X)
                
                
                #print("team", team, "i", i)

                # Save the group_frame, playertext1, and playerbutton in each for loop with the team name as key
                self.spiel_buttons[team_id][i] = (self.group_frame, playertext1, playertext2, playertext3, playerbutton1, playerbutton2)  # Use append for a list
                
                #self.spiel_buttons[team] = (playerbutton)  # Use append for a list


        self.manual_team_select_1 = ttk.Combobox(manual_manual_frame, values=self.read_teamNames(), font=("Helvetica", 14))
        self.manual_team_select_1.pack(pady=10, side=tk.BOTTOM, anchor=tk.S)
        self.manual_team_select_1.bind("<<ComboboxSelected>>", lambda event, nr=1: self.on_team_select(event, nr))
        
        
        self.manual_team_select_2 = ttk.Combobox(manual_manual_frame, values=self.read_teamNames(), font=("Helvetica", 14))
        self.manual_team_select_2.pack(pady=10, side=tk.BOTTOM, anchor=tk.S)
        self.manual_team_select_2.bind("<<ComboboxSelected>>", lambda event, nr=0: self.on_team_select(event, nr))


        self.create_matches_labels(manual_frame)


        if self.teams_playing.count(None) == 0:
            #print(self.teams_playing)
            #print(self.read_teamNames())
            self.manual_team_select_1.set(self.read_teamNames()[self.teams_playing[1]])
            self.manual_team_select_2.set(self.read_teamNames()[self.teams_playing[0]])
            
        if self.teams_playing.count(None) == 2:
            self.manual_team_select_1.state(["disabled"])
        
        if self.teams_playing.count(None) == 1:
            self.manual_team_select_1.state(["!disabled"])
            #print(self.teams_playing)
            self.manual_team_select_2.set(self.read_teamNames()[self.teams_playing[0]])        

    def on_team_select(self, event, nr):
        selected_team = event.widget.get()
        
        # Convert the value to the team index
        team_index = self.read_teamNames().index(selected_team)

        # Ensure self.teams_playing has enough elements
        while len(self.teams_playing) <= nr:
            self.teams_playing.append(None)

        # Assign the team index to the specified position
        self.teams_playing[nr] = team_index
        
        
        if self.teams_playing.count(None) == 0:
            self.manual_team_select_1.set(self.read_teamNames()[self.teams_playing[1]])
            self.manual_team_select_2.set(self.read_teamNames()[self.teams_playing[0]])
        
        #print(self.teams_playing)
        if self.teams_playing.count(None) == 1:
            self.manual_team_select_1.state(["!disabled"])
            #print(self.teams_playing)
            self.manual_team_select_2.set(self.read_teamNames()[self.teams_playing[0]])
            
        
        
        if self.teams_playing.count(None) == 2:
            self.manual_team_select_1.state(["disabled"])
            
        
        
        self.reload_button_command_common(self.SPIEL_frame, self.create_SPIEL_elements)

        
    def delete_all_in_frame(self, frame):
        if frame.winfo_exists():
            for widget in frame.winfo_children():
                if widget.winfo_class() == 'Frame':
                    # Recursively delete widgets in nested frames
                    widget.grid_forget()
                    widget.pack_forget()
                    self.delete_all_in_frame(widget)
                    widget.destroy()
                else:
                    widget.destroy()

            # Update the layout
            frame.update_idletasks()
            frame.update()

    
    def reload_button_command_common(self, frame, create_function_name):
        # Delete all entry fields
        self.delete_all_in_frame(frame)
        
        # Read the names from the file and put them into the entry fields
        self.create_function_name = create_function_name
        
        self.create_function_name()
        

    def player_scored_a_point(self, teamID, player_id, player_index, direction="UP"):
        # Get the current score
        print(self.read_player_stats(teamID, True, player_id)) 
        current_goals = self.read_player_stats(teamID, True, player_id)[0][2]
        
        # Update the score
        if direction == "UP":
            current_goals += 1
        else:
            current_goals -= 1
        
        start_time = time.time()
        
        # Update the score label
        self.spiel_buttons[teamID][player_index][3].config(text=f"Tore {current_goals}")

        
        
        print("Write", "teamID", teamID, "player_index", player_id)
        
        updateGoals = """
        UPDATE playerData
        SET goals = ?
        WHERE teamId = ? AND id = ?
        """
        self.cursor.execute(updateGoals, (current_goals, teamID, player_id))
        
        # Commit the changes to the database
        self.connection.commit()
        
        # Close the database self.connection
        
        
        # Record the end time
        end_time = time.time()

        # Calculate the elapsed time in milliseconds
        elapsed_time_ms = (end_time - start_time) * 1000

        # Print the result
        print(f"Elapsed Time: {elapsed_time_ms:.2f} ms")
        
        ###self.updated_data.update({"SPIEL": {team: self.read_team_names_player(team)}})
    
    
    def create_matches_labels(self, frame):
        matches = self.calculate_matches()
        
        spiel_select_frame = ttk.Frame(frame)
        spiel_select_frame.pack(pady=10, padx=10, anchor=tk.SW, side=tk.LEFT)
        
        spiel_select = ttk.Combobox(spiel_select_frame, font=("Helvetica", 14), width=35)
        spiel_select.pack(pady=10, side=tk.TOP, anchor=tk.N)

        spiel_select.bind("<<ComboboxSelected>>", lambda event: self.on_match_select(event, matches))
    
        # Initialize the values as an empty list
        values_list = []

        for match in matches:
            # Append each match label to the values list
            values_list.append(match["number"] + ": " + match["teams"][0] + " vs " + match["teams"][1])

        # Set the values of the Combobox after the loop
        spiel_select["values"] = values_list
        
        # get the index of the match that is currently being played and set the Combobox value to that match without using self.match_count - 1
        
        for match in matches:
            match_teams_indexes = [self.read_teamNames().index(match_team) for match_team in match["teams"]]
            if match_teams_indexes == self.teams_playing or match_teams_indexes[::-1] == self.teams_playing:
                se = match["number"]
                #print("got it")
                break
            #print(match["teams"], self.teams_playing, match["number"], match_teams_indexes, match_teams_indexes[::-1])
        else:
            if self.teams_playing.count(None) == 0:
                values_list = []
                values_list.append("No Match found")
                spiel_select["values"] = values_list
                spiel_select.set(values_list[0])
                print("no match found")
                return
        
        if self.teams_playing.count(None) == 0:
            
            se = int(se.replace("Spiel ", "")) - 1
            current_match_index = se
            spiel_select.set(values_list[current_match_index])
            
            
        
        next_match_button = ttk.Button(spiel_select_frame, text="Next Match", command=lambda : self.next_previous_match_button(spiel_select, matches))
        next_match_button.pack(pady=10, padx=5, side=tk.LEFT, anchor=tk.SW)
        
        previous_match_button = ttk.Button(spiel_select_frame, text="Previous Match", command=lambda : self.next_previous_match_button(spiel_select, matches, False))
        previous_match_button.pack(pady=10, padx=5, side=tk.RIGHT, anchor=tk.SE)


    def on_match_select(self, event, matches):
        selected_match = event.widget.get()
        #print(selected_match)
        #print(matches)
        # Convert the value to the match index
        match_index = [match["number"] + ": " + match["teams"][0] + " vs " + match["teams"][1] for match in matches].index(selected_match)

        # Get the teams playing in the selected match and if there are none, set teams_playing to None
        team_names = self.read_teamNames()
        
        team1_index = team_names.index(matches[match_index]["teams"][0])
        team2_index = team_names.index(matches[match_index]["teams"][1])

        if team1_index and team2_index:
            self.teams_playing = [team1_index, team2_index]
        else:
            self.teams_playing = [None, None]
            
        # Update the buttons
        self.reload_button_command_common(self.SPIEL_frame, self.create_SPIEL_elements)
        #print("match selected")
        
    
    def next_previous_match_button(self, spiel_select, matches, next_match=True):
        try:
            # Get the current match index
            current_match_index = [match["number"] + ": " + match["teams"][0] + " vs " + match["teams"][1] for match in matches].index(spiel_select.get()) + 1

            # Calculate the new match index
            new_match_index = current_match_index + 1 if next_match else current_match_index - 1

            # Ensure the new index is within bounds
            new_match_index = max(1, min(new_match_index, len(matches)))

            # Get the teams playing in the selected match
            team_names = self.read_teamNames()
            teams_playing = [team_names.index(matches[new_match_index - 1]["teams"][0]), team_names.index(matches[new_match_index - 1]["teams"][1])] if new_match_index > 0 else [None, None]

            # Update the buttons
            self.teams_playing = teams_playing
            self.reload_button_command_common(self.SPIEL_frame, self.create_SPIEL_elements)

        except ValueError:
            # Handle the case where the selected match is not found in the list
            print("Selected match not found in the list.")



    def global_scored_a_point(self, teamID, direction="UP"):
        # Get the current score
        current_score = int(self.read_team_active_goals(teamID))
        
        # Update the score
        if direction == "UP":
            current_score += 1
        else:
            current_score -= 1
            
        self.write_score_for_team_into_file(teamID, current_score)
    

        # Update the score label
        self.spiel_buttons[teamID]["global"][1].config(text=teamID + " " + str(current_score))
       
        
    def write_score_for_team_into_file(self, teamID, goals):
        
        
        updateGoals = """
        UPDATE teamData
        SET goals = ?
        WHERE id = ?
        """
        self.cursor.execute(updateGoals, (goals, teamID))
        
        
        self.connection.commit()
        
            
    
    def read_team_stats(self, team_name, stat):
        score = self.read_teamNames(self.teams_playing, True)
        score = score[score.index(team_name) + 1]
        if stat == "score":
            return score
        
    
    
##############################################################################################

##############################################################################################

    #def create_contact_elements(self):
        # Create elements for the Contact frame
        #contact_button = tk.Button(self.contact_frame, text="Contact Button", command=self.contact_button_command)
        #contact_button.pack(pady=10)
        

##############################################################################################

    def show_frame(self, frame):
        # Hide all frames and pack the selected frame
        for frm in [self.Team_frame, self.player_frame, self.SPIEL_frame]: # self.contact_frame
            frm.pack_forget()
        frame.pack(fill=tk.BOTH, expand=True)

    def show_Team_frame(self):
        self.reload_button_command()
        self.show_frame(self.Team_frame)

    def show_player_frame(self):
        self.reload_button_player_command()
        self.show_frame(self.player_frame)

    def show_SPIEL_frame(self):
        self.reload_button_command_common(self.SPIEL_frame, self.create_SPIEL_elements)
        #print(stored_data)
        self.calculate_matches()
        self.show_frame(self.SPIEL_frame)

    #def show_contact_frame(self):
        #self.show_frame(self.contact_frame)

    # Button command functions

    #def player_button_command(self):
        #print("player Button Clicked")

    #def SPIEL_button_command(self):
        #print("SPIEL Button Clicked")

    #def contact_button_command(self):
        #print("Contact Button Clicked")
        
    ##############################################################################################
            
    def test(self):
        print("test")
        
    def delete_updated_data(self):
        #print("delete")
        #print(self.updated_data)
        self.updated_data = {}
        
    ##############################################################################################
    #############################Calculatre###########################################
    ##############################################################################################
    ##############################################################################################
    def calculate_matches(self):
        
        self.match_count = 0

        initial_data = {
        "Teams": self.read_teamNames(),
        "Tore": ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
        "ZeitIntervall": 10,
        "Startzeit": [9,30],
        "LastUpdate": 0
    }
        
        teams = initial_data["Teams"][:]  # Create a copy of the teams array
        teams.pop(0)
        # If the number of teams is odd, add a "dummy" team
        if len(teams) % 2 != 0:
            teams.append("dummy")

        teams.sort()

        midpoint = (len(teams) + 1) // 2
        group1 = teams[:midpoint]
        group2 = teams[midpoint:]

        matches1 = self.calculate_matches_for_group(group1, "Gruppe 1")
        matches2 = self.calculate_matches_for_group(group2, "Gruppe 2")

        matches = self.interleave_matches(matches1, matches2)
        
        self.match_count = 0

        self.matches = list(map(lambda match: self.add_match_number(match), matches))
        
        #print(self.matches)
        
        return self.matches
    
    
    
    def interleave_matches(self, matches1, matches2):
        matches = []
        i = j = 0
        while i < len(matches1) or j < len(matches2):
            if i < len(matches1):
                matches.append(matches1[i])
                i += 1
            if j < len(matches2):
                matches.append(matches2[j])
                j += 1
        return matches


    def calculate_matches_for_group(self, teams, group_name):
        rounds = []

        for _ in range(len(teams) - 1):
            rounds.append([])
            for match in range(len(teams) // 2):
                team1 = teams[match]
                team2 = teams[-1 - match]
                rounds[-1].append([team1, team2])
            # Rotate the teams for the next round
            teams[1:1] = [teams.pop()]

        # Remove matches with the "dummy" team
        if "dummy" in teams:
            rounds = list(map(lambda rnd: list(filter(lambda match: "dummy" not in match, rnd)), rounds))

        matches = [match for rnd in rounds for match in rnd]

        matches = list(map(lambda match: {"number": "", "teams": match, "group": group_name}, matches))

        return matches


    def add_match_number(self, match):
         
        self.match_count += 1
        match["number"] = "Spiel " + str(self.match_count)
        return match


    ##############################################################################################
    ##############################################################################################
    ##############################################################################################
    ##############################################################################################
    
def get_data_for_website(which_data=-1):
    
    if which_data == 0:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        
        getTeams = """
        SELECT teamName FROM teamData
        ORDER BY id ASC
        """
        cursor.execute(getTeams)
        
        teamNames = []
        
        for team in cursor.fetchall():
            teamNames.append(team[0])
        
        teamNames.pop(0)
            
        cursor.close()
        connection.close()
        
        return teamNames
        

def get_initial_data(template_name):
    global initial_data
    tkapp.test()
    initial_data = {
        "Teams": get_data_for_website(0),
        "Tore": ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
        "ZeitIntervall": 10,
        "Startzeit": [9,30],
        "LastUpdate": 0
    }
    return make_response(render_template(template_name, initial_data=initial_data))

@app.route("/")
def index():
    return get_initial_data("websitegroup.html")

@app.route("/tree")
def tree_index():
    return get_initial_data("websitetree.html")

@app.route("/plan")
def plan_index():
    return get_initial_data("websiteplan.html")

#create fake data for testing for ZeitIntervall, Startzeit 


@app.route('/update_data')
def update_data():
    
    timeatstart = time.time()
    
    last_data_update = request.headers.get('Last-Data-Update', 0)
    #print(last_data_update)
    
    updated_data = tkapp.updated_data
    
    
    if updated_data != {}:
        
        #print(updated_data)  
        #print(updated_data.keys())
        #print(updated_data.values())
        for key, value in updated_data.items():
            for key2, value2 in stored_data.items():
                if key in value2.keys():
                    stored_data.pop(key2)
                    break
            
            stored_data.update({time.time()+2:{key:value}})
            #print(stored_data)
        
        updated_data.update({"LastUpdate": timeatstart})
        
    for key, value in stored_data.items():
        #print("magucken")
        if key >= float(last_data_update):
            #print("key", key, "value", value, "last_data_update", last_data_update, "should be updated")
            updated_data.update(value)
            #print("updated_data", updated_data)
            
    
    #print("stored_data", stored_data, "updated_data", updated_data, "last_data_update", last_data_update)
        
    #print(updated_data)
    tkapp.delete_updated_data()
    #updated_data = {'Teams': tkapp.read_team_names(), 'Players': {"Player1":"Erik Van Doof","Player2":"Felix Schweigmann"}}  # You can modify this data as needed
    return jsonify(updated_data)

global tkapp
global server_thread
global stored_data
global initial_data
global db_path

db_path = "data/data.db"
stored_data = {}
tkapp = Window(False)

if __name__ == "__main__":
    tkapp.mainloop()