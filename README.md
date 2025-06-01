# fehtcher
A python script for fetching data from the FEH wiki\n
Launch fehtcher.bat and let the fehtcher do the work!\n
This script will download heroes data as well as their icons.\n
Everything will be save in the "database" folder. It will be created at the same location as the .bat\n

Fetching is designed to only download heroes that are not already in the database.\n
So if you launch the .bat at a later date, it will only upload the newest heroes.\n
Any hero with a refine (and consequently remix) will also get updated.\n

Data is saved in multiple .csv and Heroes lists are saved in .txt.\n
I was tempted to export data as .json but I chose .csv for decoding speed.\n
I'm not sure if it makes a huge difference or not, I didn't benchmark to be honest.\n

This is part of a larger project. I will use the data fetch for various serch functionnalities\n