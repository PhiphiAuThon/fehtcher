# fehtcher
A python script for fetching data from the FEH wiki. Launch fehtcher.bat and let the fehtcher do the work!

This script will download heroes data as well as their icons.
Everything is saved in the "database" folder. It will be created at the same location as the .bat

Fetching is designed to only download heroes that are not already in the database.
So if you launch the .bat at a later date, it will only upload the newest heroes.
Any hero with a refine (and consequently remix) will also get updated.


Data is saved in multiple .csv and Heroes lists are saved in .txt.
I was tempted to export data as .json but I chose .csv for decoding speed.
I'm not sure if it makes a huge difference or not, I didn't benchmark to be honest.


This is part of a larger project. I will use the data fetch for various search functionnalities.