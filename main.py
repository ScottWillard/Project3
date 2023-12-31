import threading
import wx
import pandas as pd
import time

# Replace 'your_dataset.csv' with the actual path to your CSV file
file_path = r'game_data.csv'

# Read the dataset into a pandas DataFrame
# Specify dtype option to handle DtypeWarning
df = pd.read_csv(file_path, dtype={'genres': str}, low_memory=False)

# Create an empty graph as a dictionary
graph = {}

# Function to build the graph with loading bar
def build_graph_with_loading_bar(progress_bar, progress_label):
    progress_label.SetLabel("Graph is being built...")
    loading_length = len(df)
    chunk_size = max(1, loading_length // 100)  # Split the data into 100 chunks
    progress_bar.SetRange(loading_length)
    progress_bar.SetValue(0)

    for i in range(0, loading_length, chunk_size):
        chunk_df = df.iloc[i:i + chunk_size]
        for _, row in chunk_df.iterrows():
            game_name = row['name']
            genres = row['genres']
            if pd.notna(game_name) and pd.notna(genres):
                genres = genres.split('||')  # If there are multiple genres, split them
                for genre in genres:
                    if genre not in graph:
                        graph[genre] = []
                    graph[genre].append(game_name)
        wx.CallAfter(progress_bar.SetValue, i + chunk_size)

    wx.CallAfter(progress_label.SetLabel, "Graph building is complete.")

# Create GUI app
class GameGraphTraversalApp(wx.Frame):

    """ =========================== CONSTRUCTORS =========================== """
    def __init__(self, *args, **kwargs):
        super(GameGraphTraversalApp, self).__init__(*args, **kwargs)
        self.InitUI()

    # Defining parameters of buttons and fields of the main GUI frame
    def InitUI(self):
        self.SetTitle("Video Game Graph Traversal")
        self.SetSize((800, 500))

        panel = wx.Panel(self)

        # Genre selection entry
        genre_label = wx.StaticText(panel, label="Select a genre:")
        self.genres = ["Puzzle", "Indie", "Arcade", "Strategy", "Massively Multiplayer", "Shooter", "Platformer",
                       "Simulation", "Adventure", "Racing", "Casual", "Educational", "Sports", "RPG", "Fighting",
                       "Family", "Board Games", "Card"]
        self.genre_var = wx.ComboBox(panel, value=self.genres[0], choices=self.genres, style=wx.CB_READONLY)

        # Build Graph button
        build_graph_button = wx.Button(panel, label="Build Graph", size=(150, -1))
        build_graph_button.Bind(wx.EVT_BUTTON, self.OnBuildGraph)

        # Progress bar for graph building
        self.graph_progress_label = wx.StaticText(panel, label="")
        self.graph_progress_bar = wx.Gauge(panel, range=1, size=(500, 25))

        # Start Traversals buttons
        bfs_button = wx.Button(panel, label="Breadth First Search", size=(150, -1))
        bfs_button.Bind(wx.EVT_BUTTON, self.OnStartBFS)
        dfs_button = wx.Button(panel, label="Depth First Search", size=(150, -1))
        dfs_button.Bind(wx.EVT_BUTTON, self.OnStartDFS)

        # Progress bars for BFS and DFS traversals
        self.bfs_progress_label = wx.StaticText(panel, label="Breadth First Search")
        self.bfs_progress_bar = wx.Gauge(panel, range=1, size=(500, 25))
        self.dfs_progress_label = wx.StaticText(panel, label="Depth First Search")
        self.dfs_progress_bar = wx.Gauge(panel, range=1, size=(500, 25))

        # Output text box (to show BFS and DFS traversal results)
        self.result_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)

        # Clear Results button
        clear_results_button = wx.Button(panel, label="Clear Results", size=(150, -1))
        clear_results_button.Bind(wx.EVT_BUTTON, self.OnClearResults)

        # Sizers for layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        genre_sizer = wx.BoxSizer(wx.HORIZONTAL)
        graph_sizer = wx.BoxSizer(wx.VERTICAL)
        bfs_sizer = wx.BoxSizer(wx.VERTICAL)
        dfs_sizer = wx.BoxSizer(wx.VERTICAL)
        clear_button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        genre_sizer.Add(genre_label, proportion=0, flag=wx.ALL, border=5)
        genre_sizer.Add(self.genre_var, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)

        graph_sizer.Add(build_graph_button, proportion=0, flag=wx.ALL | wx.EXPAND, border=5)
        graph_sizer.Add(self.graph_progress_label, proportion=0, flag=wx.LEFT | wx.BOTTOM, border=5)
        graph_sizer.Add(self.graph_progress_bar, proportion=0, flag=wx.ALL | wx.EXPAND, border=5)

        bfs_sizer.Add(bfs_button, proportion=0, flag=wx.ALL | wx.EXPAND, border=5)
        bfs_sizer.Add(self.bfs_progress_label, proportion=0, flag=wx.ALL | wx.EXPAND, border=5)
        bfs_sizer.Add(self.bfs_progress_bar, proportion=0, flag=wx.ALL | wx.EXPAND, border=5)

        dfs_sizer.Add(dfs_button, proportion=0, flag=wx.ALL | wx.EXPAND, border=5)
        dfs_sizer.Add(self.dfs_progress_label, proportion=0, flag=wx.ALL | wx.EXPAND, border=5)
        dfs_sizer.Add(self.dfs_progress_bar, proportion=0, flag=wx.ALL | wx.EXPAND, border=5)

        clear_button_sizer.Add(clear_results_button, proportion=0, flag=wx.ALL | wx.EXPAND, border=5)

        sizer.Add(genre_sizer, proportion=0, flag=wx.EXPAND)
        sizer.Add(graph_sizer, proportion=0, flag=wx.EXPAND)
        sizer.Add(bfs_sizer, proportion=0, flag=wx.EXPAND)
        sizer.Add(dfs_sizer, proportion=0, flag=wx.EXPAND)
        sizer.Add(self.result_text, proportion=1, flag=wx.EXPAND)
        sizer.Add(clear_button_sizer, proportion=0, flag=wx.EXPAND)

        panel.SetSizer(sizer)



    """ =========================== NESTED CLASS =========================== """
    # Defining parameters of the GUI frame that displays information on the traversed games
    class ResultingList(wx.Frame):
        def __init__(self, title, parent):
            wx.Frame.__init__(self, parent=parent, title=title, size=(800, 500))
            main_sizer = wx.BoxSizer(wx.VERTICAL)
            self.row_obj_dict = {}

            self.list_ctrl = wx.ListCtrl(
                self, size=(-1, 500),
                style=wx.LC_REPORT | wx.BORDER_SUNKEN
            )

            self.list_ctrl.InsertColumn(0, 'Name', width=600)
            self.list_ctrl.InsertColumn(1, 'Genre', width=200)

            main_sizer.Add(self.list_ctrl, 0, wx.ALL | wx.EXPAND, 5)

            self.SetSizer(main_sizer)

        def update_game_list(self, games_data):

            self.list_ctrl.DeleteAllItems()  # Clear previous items (if any)

            index = 0

            for game_name, genre in games_data:
                self.list_ctrl.InsertItem(index, game_name)
                self.list_ctrl.SetItem(index, 1, genre)
                index += 1

        def show_game_results(self):
            self.Show()



    """ =========================== GETTERS =========================== """
    # Getter function that returns what genre has been selected for traversal
    def get_genre(self):
        return self.genre_var.GetValue()



    """ =========================== MUTATORS =========================== """
    # FIXME: anyway to do this during traversal instead of after the fact?
    # Function adds names and genres of the games/nodes traversed in the graph to a list, for later displaying
    def generate_results_list(self, traversal_type):

        selected_genre = self.genre_var.GetValue()

        # title = '{} Games'.format(selected_genre)
        title = '{} - {} Games'.format(traversal_type, selected_genre)
        results_list = self.ResultingList(title, parent=wx.GetTopLevelParent(self))

        games_data = [(game_name, selected_genre) for game_name in graph.get(selected_genre, [])]

        results_list.update_game_list(games_data)  # Pass the game data to the function

        return results_list

    # Called when "Build Graph" button is pressed; generates graph from information in plaintext .csv file
    def OnBuildGraph(self, event):
        self.graph_progress_bar.SetValue(0)
        graph_building_thread = threading.Thread(target=build_graph_with_loading_bar,
                                                 args=(self.graph_progress_bar, self.graph_progress_label))
        graph_building_thread.start()

    # Called when user decides to clear the list of previous traversal results
    def OnClearResults(self, event):
        self.result_text.Clear()



    """ =========================== BFS TRAVERSAL IMPLEMENTATION =========================== """
    # Function called upon clicking the BFS button in main GUI frame
    def OnStartBFS(self, event):
        self.result_text.AppendText("Breadth First Search Traversal of {} Games:\n".format(self.genre_var.GetValue()))
        self.result_text.AppendText("---------------------------------------\n")
        results_list = self.generate_results_list("Breadth First")
        self.bfs_traversal(graph.get(self.genre_var.GetValue(), []), "", results_list)

    # This is the function called from OnStartBFS; creates a separate thread that then calls its bfs_helper function
    def bfs_traversal(self, starting_nodes, result_text, results_list):
        self.bfs_progress_bar.SetRange(len(starting_nodes))
        bfs_thread = threading.Thread(target=self.bfs_helper, args=(starting_nodes, result_text, results_list))
        bfs_thread.start()

    # Function is called from bfs_traversal, returns information on nodes to user in main frame, and generates list
    # of nodes traversed
    def bfs_helper(self, starting_nodes, result_text, resulting_list_frame):
        start_time = time.time()
        queue = []
        bfs_games_traversed = set()

        interval = 0.0001
        for node in starting_nodes:
            time.sleep(interval)  # Adjust the interval for responsiveness
            if node not in bfs_games_traversed:
                bfs_games_traversed.add(node)
                related_nodes = graph.get(node, [])
                queue.extend(related_nodes)

                # this block of code controls the updating of the BFS progress bar
                current_nodes = len(bfs_games_traversed)
                progress_value = current_nodes
                wx.CallAfter(self.bfs_progress_bar.SetValue, progress_value)


        total_nodes = len(bfs_games_traversed)

        num_intervals = 100

        for i in range(num_intervals + 1):
            if i < num_intervals:
                # Perform traversal for remaining nodes at each interval
                for _ in range(int(total_nodes / num_intervals)):
                    if not queue:
                        break
                    node = queue.pop(0)
                    if node not in bfs_games_traversed:
                        bfs_games_traversed.add(node)
                        related_nodes = graph.get(node, [])
                        queue.extend(related_nodes)



        end_time = time.time()
        bfs_time_elapsed = end_time - start_time
        result_text += f"Breadth First Search Time Elapsed: {bfs_time_elapsed:.2f} Seconds\n"
        result_text += f"Traversed {len(bfs_games_traversed)} {self.get_genre()} games\n\n"

        wx.CallAfter(resulting_list_frame.show_game_results)

        wx.CallAfter(self.result_text.AppendText, result_text)



    """ =========================== DFS TRAVERSAL IMPLEMENTATION =========================== """
    # Function called upon clicking the DFS button in main GUI frame
    def OnStartDFS(self, event):
        self.result_text.AppendText("Depth First Search Traversal of {} Games:\n".format(self.genre_var.GetValue()))
        self.result_text.AppendText("---------------------------------------\n")
        results_list = self.generate_results_list("Depth First")
        self.dfs_traversal(graph.get(self.genre_var.GetValue(), []), "", results_list)

    # This is the function called from OnStartDFS; creates a separate thread that then calls its dfs_helper function
    def dfs_traversal(self, starting_nodes, result_text, results_list):
        self.dfs_progress_bar.SetRange(len(starting_nodes))
        dfs_thread = threading.Thread(target=self.dfs_helper, args=(starting_nodes, result_text, results_list))
        dfs_thread.start()

    # Function is called from dfs_traversal, returns information on nodes to user in main frame, and generates list
    def dfs_helper(self, starting_nodes, result_text, resulting_list_frame):
        start_time = time.time()
        dfs_games_traversed = set()

        interval = 0.0001  # Update interval in seconds (adjust as needed)

        def dfs_recursive(node):
            if node not in dfs_games_traversed:
                dfs_games_traversed.add(node)

                # this block of code controls the updating of the DFS progress bar
                current_nodes = len(dfs_games_traversed)
                progress_value = current_nodes  # Convert to integer
                wx.CallAfter(self.dfs_progress_bar.SetValue, progress_value)  # Update progress bar
                time.sleep(interval)  # Adjust the interval for responsiveness

                related_nodes = graph.get(node, [])
                for related_node in related_nodes:
                    dfs_recursive(related_node)

        total_nodes = len(starting_nodes)

        num_intervals = 100

        for i in range(num_intervals + 1):
            if i < num_intervals:
                # Perform traversal for remaining nodes at each interval
                for node in starting_nodes:
                    dfs_recursive(node)

        end_time = time.time()
        dfs_time_elapsed = end_time - start_time
        result_text += f"Depth First Search Time Elapsed: {dfs_time_elapsed:.2f} Seconds\n"
        result_text += f"Traversed {len(dfs_games_traversed)} {self.get_genre()} games\n\n"

        wx.CallAfter(resulting_list_frame.show_game_results)

        wx.CallAfter(self.result_text.AppendText, result_text)



def main():
    app = wx.App()
    frame = GameGraphTraversalApp(None)
    frame.Show()
    app.MainLoop()


if __name__ == "__main__":
    main()