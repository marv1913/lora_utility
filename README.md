
# LORA Utility
This application implements a self designed multi hop [routing protocol](https://github.com/marv1913/lora_utility/wiki). The application was designed for a  Ting-01 SX1278 LoRa module. To demonstrate the functionality of the protocol a messenger was implemented, too. 

## Deployment

    

 1. Install requirements:
 
     ``python3 -m pip install -r requirements.txt``
2.  Edit the variable file which is located under ``resources/util/variables.py`` (optional step).
3.  Start the application:

    ``python3 resources/main.py``

## CLI Usage
There are two different mode:
1. config mode
- enter config mode typing ``:c``
- get current destination address: ``?``
- to set another destination address just type in the address and hit enter
- get all available destination adresses: ``all``
- set module configuration defined in variables file: ``config``
2.  send mode:
 - enter send mode typing ``:s``
 - here you can send messages to receiver set in config mode (type message and press enter)
 - see current state of the routing table: ``:l``
 

	
