# System Monitoring and Analysis Tools

## Introduction

This repository contains two Python applications designed for system monitoring and subsequent analysis. The first application, `monitor.py`, collects real-time system metrics like CPU, GPU, and RAM usage, as well as disk read and write speeds. It stores this data in a SQLite database. The second application, `analyzer.py`, reads the data from the database and displays it in various graphical formats.

## Installation

1. Clone the repository or download the ZIP file.
2. Navigate to the project folder and install the required Python packages:

    ```
    pip install -r requirements.txt
    ```

3. Additionally you can create exe files using pyinstaller

    ```
    pip install pyinstaller

    pyinstaller --onefile monitor.py
    pyinstaller --onefile analyzer.py
    ```

## Usage

### monitor.py

1. Navigate to the project folder in your terminal.
2. Run `monitor.py`:

    ```
    python monitor.py
    ```

-   This will start collecting system metrics and store them in a SQLite database named `system_metrics.db`.
-   The application also provides a Tkinter GUI that shows the real-time metrics.

#### Features

-   Real-time monitoring of CPU, GPU, RAM usage.
-   Real-time monitoring of disk read and write speeds.
-   Data is stored in a SQLite database for further analysis.

### analyzer.py

1. Navigate to the project folder in your terminal.
2. Run `analyzer.py`:

    ```
    python analyzer.py
    ```

-   This will open a Tkinter application where you can select the time range for which you want to analyze the metrics.

#### Features

-   Ability to filter metrics by the last hour, day, or week.
-   Visual presentation of metrics in the form of line graphs.

## Dependencies

-   Python 3.x
-   Tkinter
-   SQLite3
-   Pandas
-   Matplotlib
-   psutil
-   GPUtil

## License

This project is open-source and available under the MIT License.
