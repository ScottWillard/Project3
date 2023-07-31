import threading
import wx
import pandas as pd
import time

# Replace 'your_dataset.csv' with the actual path to your CSV file
file_path = r'game_info.csv'

# Read the dataset into a pandas DataFrame
# Specify dtype option to handle DtypeWarning
df = pd.read_csv(file_path, dtype={'genres': str}, low_memory=False)

# Create an empty graph as a dictionary
graph = {}


# Function to build the graph with loading bar
def build_graph_with_loading_bar(progress_bar, progress_label):
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
    def __init__(self, *args, **kwargs):
        super(GameGraphTraversalApp, self).__init__(*args, **kwargs)

        self.InitUI()

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
        self.graph_progress_label = wx.StaticText(panel, label="Graph is being built...")
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

    def OnBuildGraph(self, event):
        self.graph_progress_bar.SetValue(0)
        graph_building_thread = threading.Thread(target=build_graph_with_loading_bar,
                                                 args=(self.graph_progress_bar, self.graph_progress_label))
        graph_building_thread.start()

    def bfs_traversal(self, starting_nodes, result_text):
        start_time = time.time()
        queue = []
        bfs_games_traversed = set()

        for node in starting_nodes:
            if node not in bfs_games_traversed:
                bfs_games_traversed.add(node)
                related_nodes = graph.get(node, [])
                queue.extend(related_nodes)

        total_nodes = len(bfs_games_traversed)
        interval = 0.1
        num_intervals = 100

        for i in range(num_intervals + 1):
            current_nodes = len(bfs_games_traversed)
            progress_value = int((current_nodes / total_nodes) * 100)
            wx.CallAfter(self.bfs_progress_bar.SetValue, progress_value)
            time.sleep(interval)  # Adjust the interval for responsiveness
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
        result_text += f"Traversed {len(bfs_games_traversed)} {self.genre_var.GetValue()} games\n\n"

        wx.CallAfter(self.result_text.AppendText, result_text)

    def dfs_traversal(self, starting_nodes, result_text):
        start_time = time.time()
        dfs_games_traversed = set()

        def dfs_recursive(node):
            if node not in dfs_games_traversed:
                dfs_games_traversed.add(node)
                related_nodes = graph.get(node, [])
                for related_node in related_nodes:
                    dfs_recursive(related_node)

        total_nodes = len(starting_nodes)
        interval = 0.1  # Update interval in seconds (adjust as needed)
        num_intervals = 100

        for i in range(num_intervals + 1):
            current_nodes = len(dfs_games_traversed)
            progress_value = int((current_nodes / total_nodes) * 100)  # Convert to integer
            wx.CallAfter(self.dfs_progress_bar.SetValue, progress_value)  # Update progress bar
            time.sleep(interval)  # Adjust the interval for responsiveness
            if i < num_intervals:
                # Perform traversal for remaining nodes at each interval
                for node in starting_nodes:
                    dfs_recursive(node)

        end_time = time.time()
        dfs_time_elapsed = end_time - start_time
        result_text += f"Depth First Search Time Elapsed: {dfs_time_elapsed:.2f} Seconds\n"
        result_text += f"Traversed {len(dfs_games_traversed)} {self.genre_var.GetValue()} games\n\n"

        wx.CallAfter(self.result_text.AppendText, result_text)

    def OnStartBFS(self, event):
        self.result_text.AppendText("Breadth First Search Traversal of {} Games:\n".format(self.genre_var.GetValue()))
        self.result_text.AppendText("---------------------------------------\n")
        self.bfs_traversal(graph.get(self.genre_var.GetValue(), []), "")

    def OnStartDFS(self, event):
        self.result_text.AppendText("Depth First Search Traversal of {} Games:\n".format(self.genre_var.GetValue()))
        self.result_text.AppendText("---------------------------------------\n")
        self.dfs_traversal(graph.get(self.genre_var.GetValue(), []), "")

    def OnClearResults(self, event):
        self.result_text.Clear()


def main():
    app = wx.App()
    frame = GameGraphTraversalApp(None)
    frame.Show()
    app.MainLoop()


if __name__ == "__main__":
    main()
