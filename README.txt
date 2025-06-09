System Stats App - Quick Guide
This application displays statistics about your CPU, Memory, Disk, Battery, Network, and GPU.
Click the "Export to TXT" button to save a text file of the current statistics. 

NOTE: 'CPU Temperature' and 'Fan Speed' stats are not supported on Windows.

On Windows:
1. Double-click SystemStatsApp.exe to launch.
2. No installations or commands required. Just run and use!

On Linux:
1. Make sure you have Python installed.
2. Download the system_stats_app.py file.
3. Install this package: "pip install pyqt5 psutil"
4. Run "python system_stats_app.py" in the command line.
5. To enable sensors for temperature and fan speed data, run these commands in order, while saying “Yes” (or just pressing Enter) to default prompts: 
	'sudo apt install lm-sensors'
	'sudo sensors-detect'
	'sudo service kmod start'

On MacOS:
1. Make sure you have Python installed.
2. Download the system_stats_app.py file.
3. Install this package: "pip install pyqt5 psutil"
4. Run "python system_stats_app.py" in the command line.
