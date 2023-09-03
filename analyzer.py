"""
System Metrics Plotter

This script plots system metrics collected by the system monitoring tool.
It provides options to filter the data by different time periods like the last hour, last day, and last week.
"""

from datetime import datetime, timedelta
import sqlite3

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd


def fetch_data_from_db(db_name: str) -> pd.DataFrame:
    """
    Fetch data from SQLite database and return as a DataFrame.

    Parameters:
        db_name (str): The name of the SQLite database file.

    Returns:
        pd.DataFrame: DataFrame containing the fetched data.
    """
    conn = sqlite3.connect(db_name)
    df = pd.read_sql_query("SELECT * from metrics", conn)
    conn.close()
    return df


def filter_time(df: pd.DataFrame, time_period: str) -> pd.DataFrame:
    """
    Filters the data based on the selected time period.

    Parameters:
        df (pd.DataFrame): The original DataFrame containing system metrics.
        time_period (str): The time period selected ("Last Hour", "Last Day", "Last Week").

    Returns:
        pd.DataFrame: The filtered DataFrame.
    """
    now = datetime.now()
    if time_period == "Last Hour":
        past_time = now - timedelta(hours=1)
    elif time_period == "Last Day":
        past_time = now - timedelta(days=1)
    elif time_period == "Last Week":
        past_time = now - timedelta(weeks=1)
    elif time_period == "All":
        return df
    return df[df.index >= past_time]


def plot_metric_subplot(
    df: pd.DataFrame, metric: str, subplot_position: int, title: str, ylabel: str, color: str = "b"
) -> None:
    """
    Plot a single metric on a given subplot position.

    Parameters:
        df (pd.DataFrame): The DataFrame containing the data.
        metric (str): The name of the metric to plot.
        subplot_position (int): The position of the subplot.
        title (str): The title of the subplot.
        ylabel (str): The y-axis label of the subplot.
        color (str, optional): The color of the plot. Defaults to 'b' (blue).
    """
    plt.subplot(2, 2, subplot_position)
    plt.plot(df[metric], label=f"{ylabel}", color=color)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    plt.title(title)
    plt.xlabel("Time")
    plt.ylabel(ylabel)
    plt.legend()


def plot_graphs() -> None:
    """
    Plots graphs for CPU, GPU, RAM usage and Disk Read/Write speed based on the selected time period.
    """
    time_period = time_var.get()
    df = fetch_data_from_db("system_metrics.db")
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df.set_index("timestamp", inplace=True)

    df_filtered = filter_time(df, time_period)

    plt.figure(figsize=(14, 8))

    plot_metric_subplot(df_filtered, "cpu_percent", 1, "CPU Usage Over Time", "CPU %")
    plot_metric_subplot(df_filtered, "gpu_percent", 2, "GPU Usage Over Time", "GPU %", color="r")
    plot_metric_subplot(df_filtered, "ram_percent", 3, "RAM Usage Over Time", "RAM %", color="g")

    plt.subplot(2, 2, 4)
    plt.plot(df_filtered["read_speed"], label="Read Speed (MB/s)", color="m")
    plt.plot(df_filtered["write_speed"], label="Write Speed (MB/s)", color="c")
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    plt.title("Disk Read/Write Speed Over Time")
    plt.xlabel("Time")
    plt.ylabel("Speed (MB/s)")
    plt.legend()

    plt.tight_layout()
    plt.show()


def initialize_gui() -> tk.Tk:
    """
    Initialize Tkinter GUI and return the root window.

    Returns:
        tk.Tk: The root Tkinter window.
    """
    _root = tk.Tk()
    _root.title("System Metrics Plotter")
    _root.geometry("200x100")
    return _root


def create_controls(_root: tk.Tk, _time_var: tk.StringVar) -> None:
    """
    Create and place controls (ComboBox, Button) on the Tkinter GUI.

    Parameters:
        _root (tk.Tk): The root Tkinter window.
        _time_var (tk.StringVar): Tkinter StringVar object to hold the value of the ComboBox.
    """
    time_menu = ttk.Combobox(_root, textvariable=_time_var, values=["Last Hour", "Last Day", "Last Week", "All"])
    time_menu.pack()
    plot_button = tk.Button(_root, text="Plot Graphs", command=plot_graphs)
    plot_button.pack()


if __name__ == "__main__":
    root = initialize_gui()
    time_var = tk.StringVar()
    time_var.set("Last Hour")  # default value

    create_controls(root, time_var)

    root.mainloop()
