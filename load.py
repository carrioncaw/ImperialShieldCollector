import tkinter as tk
import logging
import l10n
import functools
import os
import math

from typing import Optional, Tuple, Dict, List, Any
from config import appname

# I made changes, chalah

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f'{appname}.{plugin_name}')

_ = functools.partial(l10n.Translations.translate, context=__file__)

label: Optional[tk.Label]
status: Optional[tk.Label]

# Events that involve a potential change in material counts
event_types: int = set(['StartUp','Materials','MaterialCollected','MaterialDiscarded','EngineerContribution','EngineerCraft','MaterialTrade','MissionCompleted','ScientificResearch','TechnologyBroker','Synthesis'])

impshield_count: Optional[int] = None
shielding_need: int = 0

# Max units per grade
grades: List[int] = [0,300,250,200,150,100]

# Trade ratios for in-row and cross trades for each grade per unit of Imperial Shielding
shielding_trades: List[int] = [0,81,27,9,3,1]
other_trades: List[float] = [0.0,(27/2),(9/2),(3/2),(1/2),(1/6)]

# Tradable materials only - Category: {Name: Grade,...},
materials_data: Dict[str,Dict[str,int]] = {
  'Chemical':{'chemicalstorageunits':1,'chemicalprocessors':2,'chemicaldistillery':3,'chemicalmanipulators':4,'pharmaceuticalisolators':5},
  'Thermic':{'temperedalloys':1,'heatresistantceramics':2,'precipitatedalloys':3,'thermicalloys':4,'militarygradealloys':5},
  'Heat':{'heatconductionwiring':1,'heatdispersionplate':2,'heatexchangers':3,'heatvanes':4,'protoheatradiators':5},
  'Conductive':{'basicconductors':1,'conductivecomponents':2,'conductiveceramics':3,'conductivepolymers':4,'biotechconductors':5},
  'Mechanical components':{'mechanicalscrap':1,'mechanicalequipment':2,'mechanicalcomponents':3,'configurablecomponents':4,'improvisedcomponents':5},
  'Capacitors':{'gridresistors':1,'hybridcapacitors':2,'electrochemicalarrays':3,'polymercapacitors':4,'militarysupercapacitors':5},
  'Shielding':{'wornshieldemitters':1,'shieldemitters':2,'shieldingsensors':3,'compoundshielding':4,'imperialshielding':5},
  'Composite':{'compactcomposites':1,'filamentcomposites':2,'highdensitycomposites':3,'fedproprietarycomposites':4,'fedcorecomposites':5},
  'Crystals':{'crystalshards':1,'uncutfocuscrystals':2,'focuscrystals':3,'refinedfocuscrystals':4,'exquisitefocuscrystals':5},
  'Alloys':{'salvagedalloys':1,'galvanisingalloys':2,'phasealloys':3,'protolightalloys':4,'protoradiolicalloys':5}
}

def plugin_start3(plugin_dir: str) -> str:
  logger.debug('Plugin loaded')
  return "ImperialShieldCollector"

def plugin_stop() -> None:
  pass

def prefs_changed(cmdr: str, is_beta: bool) -> None:
  update_status()

def plugin_app(parent) -> Tuple[tk.Label,tk.Label]:
  global label, status
  label = tk.Label(parent, text=f'{_("Imperial Shielding")}:')
  status = tk.Label(parent, text=f'Waiting for data')
  update_status()
  return (label, status)

def journal_entry(
  cmdr: str, is_beta: bool, system: str, station: str, entry: Dict[str, Any], state: Dict[str, Any]
) -> None:
  global label, status, impshield_count
  if entry['event'] in event_types:
    logger.debug(entry['event'])
    calculate_needs(state)
    update_status()

def calculate_needs(state: Dict[str, Any]) -> None:
  global materials_data, shielding_need, impshield_count, shielding_trades, other_trades, grades
  impshield_count = state['Manufactured']['imperialshielding']
  shielding_need = 100
  for category in materials_data.keys():
    for mat in materials_data[category].keys():
      if mat is not 'imperialshielding':
        # Imperial Shielding is already accounted for by starting at 100, so when everything else is full, we get N / 100 for the counter.
        grade = materials_data[category][mat]
        need = grades[grade] - state['Manufactured'][mat]
        if need > 0:
          ratio = shielding_trades[grade] if category == 'Shielding' else other_trades[grade]
          shielding_need += math.ceil(need / ratio)

def update_status() -> None:
  global label, status, impshield_count
  label["text"] = f'{_("Imperial Shielding")}:'
  if impshield_count is None:
    status["text"] = f'? / ?'
  else:
    status["text"] = f'{impshield_count} / {shielding_need}'
  logger.debug(status["text"])


