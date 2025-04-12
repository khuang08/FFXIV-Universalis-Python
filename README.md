# FFXIV-Universalis-Project
Basic scripts to fetch pricing and item sale information from Universalis

## Getting Started

To use the Python script, you can build the setup a virtual environment for necessary modules or install them directly on your machine.    

- **import requests**

You will also need Item.csv in the same folder as the location where you are running the script.

## Installation

- Download ffxiv_item_search.py and items.json to any desired location in the same folder
- Run the following command **"pip install requests"**

## Usage

You can run any of the scripts directly in Python 
 e.g. **python universalis-item-fetch-price.py**  
 - **universalis-item-fetch-price.py** will return the most recent and lowest price available for each item defined in the script. The list of items can be edited directly in the py script, please refer to **items.json** for the ID and item name.
 - **universalis-most-frequently-updated-bryn.py** will return the top 1000 items sold on the marketboard. The list of worlds and number of results can be edited directly in the py script.


## Additional Documentation and Acknowledgments

This project includes the following files sourced from external repositories:
- `items.json`

Original files are from [ffxiv-teamcraft/ffxiv-teamcraft](https://github.com/ffxiv-teamcraft/ffxiv-teamcraft), 
© [FFXIV Teamcraft](https://ffxivteamcraft.com/). These files are licensed under the **MIT License**.
