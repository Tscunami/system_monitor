"""
System resource monitoring tool and database writer.
"""

import sqlite3
from threading import Thread
import time
import tkinter as tk
from tkinter import StringVar, Frame, Label
from typing import List

import psutil
import GPUtil


BUFFER_SIZE = 60  # Number of records in the buffer before writing to the database
DB_NAME = "system_metrics.db"
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


def initialize_database() -> None:
    """
    Initialize SQLite database and create a table if it does not exist.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            cpu_percent REAL,
            gpu_percent REAL,
            ram_percent REAL,
            read_speed REAL,
            write_speed REAL
        )
        """
    )
    conn.commit()


def run_metrics() -> None:
    """
    Collects system metrics and writes them to a SQLite database.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    old_read = old_write = 0
    cpu_percentages = []
    cpu_avg_num = 8
    initial_cycle = True
    data_buffer = []

    while True:
        timestamp = time.strftime(TIMESTAMP_FORMAT)
        cpu_percent = collect_cpu_metrics(cpu_percentages, cpu_avg_num)
        gpu_percent = collect_gpu_metrics()
        ram_percent = collect_ram_metrics()
        read_speed, write_speed, old_read, old_write = collect_disk_metrics(old_read, old_write, initial_cycle)

        if initial_cycle:
            initial_cycle = False
            continue

        data_buffer.append((timestamp, cpu_percent, gpu_percent, ram_percent, read_speed, write_speed))
        update_gui(cpu_percent, gpu_percent, ram_percent, read_speed, write_speed, data_buffer)

        if len(data_buffer) >= BUFFER_SIZE:
            write_to_database(c, data_buffer)
            data_buffer.clear()

        time.sleep(0.5)


def collect_cpu_metrics(cpu_percentages: List[float], cpu_avg_num: int) -> float:
    """
    Collect and average CPU metrics.

    Parameters:
        cpu_percentages (List[float]): A list storing the last N CPU percentages.
        cpu_avg_num (int): Number of CPU percentages to average.

    Returns:
        float: The average CPU usage.
    """
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_percentages.append(cpu_percent)
    if len(cpu_percentages) > cpu_avg_num:
        cpu_percentages.pop(0)
    return round(sum(cpu_percentages) / len(cpu_percentages), 2)


def collect_gpu_metrics() -> float:
    """
    Collect GPU metrics.

    Returns:
        float: The current GPU usage.
    """
    GPUs = GPUtil.getGPUs()
    return round(GPUs[0].load * 100, 2) if GPUs else 0.0


def collect_ram_metrics() -> float:
    """
    Collect RAM metrics.

    Returns:
        float: The current RAM usage.
    """
    return round(psutil.virtual_memory().percent, 2)


def collect_disk_metrics(old_read: int, old_write: int, initial_cycle: bool) -> tuple[int, int, int, int]:
    """
    Collect Disk metrics.

    Parameters:
        old_read (int): Previous disk read bytes.
        old_write (int): Previous disk write bytes.
        initial_cycle (bool): Flag to check if it's the first measurement cycle.

    Returns:
        tuple: Contains new read bytes, new write bytes, and their speeds.
    """
    disk_io = psutil.disk_io_counters()
    new_read = disk_io.read_bytes
    new_write = disk_io.write_bytes

    if initial_cycle:
        return 0, 0, new_read, new_write

    read_speed = round((new_read - old_read) / 1024 / 1024, 2)
    write_speed = round((new_write - old_write) / 1024 / 1024, 2)
    return read_speed, write_speed, new_read, new_write


def update_gui(
    cpu_percent: float, gpu_percent: float, ram_percent: float, read_speed: float, write_speed: float, data_buffer: list
) -> None:
    """
    Update Tkinter GUI with the collected metrics.

    Parameters:
        cpu_percent (float): Current CPU usage.
        gpu_percent (float): Current GPU usage.
        ram_percent (float): Current RAM usage.
        read_speed (float): Disk read speed.
        write_speed (float): Disk write speed.
        data_buffer (list): Buffer of data to be saved.
    """
    remaining_time.set(f"Time until next save: {BUFFER_SIZE - len(data_buffer)}s")
    cpu_label_var.set(f"{cpu_percent}%")
    gpu_label_var.set(f"{gpu_percent}%")
    ram_label_var.set(f"{ram_percent}%")
    read_speed_var.set(f"{read_speed} MB/s")
    write_speed_var.set(f"{write_speed} MB/s")


def write_to_database(cursor: sqlite3.Cursor, data_buffer: list) -> None:
    """
    Write collected metrics to the SQLite database.

    Parameters:
        cursor (sqlite3.Cursor): SQLite cursor object.
        data_buffer (list): Buffer of data to be saved.
    """
    cursor.execute("BEGIN TRANSACTION")
    cursor.executemany(
        "INSERT INTO metrics (timestamp, cpu_percent, gpu_percent, ram_percent, read_speed, write_speed) VALUES (?, ?, ?, ?, ?, ?)",
        data_buffer,
    )
    cursor.execute("COMMIT")


def initialize_gui() -> tk.Tk:
    """
    Initialize Tkinter GUI and return the root window.

    Returns:
        tk.Tk: The root Tkinter window.
    """
    _root = tk.Tk()
    _root.title("System Resource Monitoring")
    _root.geometry("220x170")
    _root.configure(bg="black")
    return _root


def create_labels(_root: tk.Tk, _variables: dict[str, StringVar]) -> None:
    """
    Create and place labels on the Tkinter GUI.

    Parameters:
        _root (tk.Tk): The root Tkinter window.
        _variables (dict): Dictionary of Tkinter StringVar objects.
    """
    bg_color = "black"
    label_color = "white"

    # Create Header Frame
    header_frame = Frame(_root, bg=bg_color)
    header_frame.pack(fill="both")
    Label(header_frame, text="Component", bg=bg_color, fg=label_color, width=15).grid(row=0, column=0)
    Label(header_frame, text="Usage", bg=bg_color, fg=label_color, width=15).grid(row=0, column=1)
    border = Frame(header_frame, bg="white", height=1)
    border.grid(row=1, columnspan=2, sticky="we")

    frames = {
        "CPU": _variables["cpu_label_var"],
        "GPU": _variables["gpu_label_var"],
        "RAM": _variables["ram_label_var"],
        "Read Speed": _variables["read_speed_var"],
        "Write Speed": _variables["write_speed_var"],
    }

    for key, value in frames.items():
        frame = Frame(_root, bg=bg_color)
        frame.pack(fill="both")
        Label(frame, text=key, bg=bg_color, fg=label_color, width=15).grid(row=0, column=0)
        Label(frame, textvariable=value, bg=bg_color, fg=label_color, width=15).grid(row=0, column=1)

    Label(_root, textvariable=_variables["remaining_time"], bg=bg_color, fg=label_color).pack(side="bottom", pady=5)


if __name__ == "__main__":
    initialize_database()

    root = initialize_gui()
    remaining_time = StringVar()
    remaining_time.set("Initializing")
    cpu_label_var = StringVar()
    gpu_label_var = StringVar()
    ram_label_var = StringVar()
    read_speed_var = StringVar()
    write_speed_var = StringVar()

    variables = {
        "remaining_time": remaining_time,
        "cpu_label_var": cpu_label_var,
        "gpu_label_var": gpu_label_var,
        "ram_label_var": ram_label_var,
        "read_speed_var": read_speed_var,
        "write_speed_var": write_speed_var,
    }
    create_labels(root, variables)

    Thread(target=run_metrics, daemon=True).start()

    root.mainloop()
