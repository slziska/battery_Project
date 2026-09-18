
from rich import print 
from tqdm import tqdm
import time
from loguru import logger
from plyer import notification
from dotenv import load_dotenv
import os

load_dotenv()

logger.add("battery_process.log")  # auto-writes to file AND terminal
logger.opt(colors=True).success("<magenta>Battery process started</magenta>")


def mixing(active_material , conductive_additive, binder, solvent):
	process = [ f"weigh out {active_material}, {conductive_additive}, {binder}, and {solvent}",
	"mix the dry ingredients together",
	f"add the {solvent} and mix thoroughly" ]
      
	return process


print("[bold hot_pink]--- Mixing ---[/bold hot_pink]")
logger.info("Started mixing")
for i,process in enumerate(mixing(os.getenv("ACTIVE_MATERIAL"), os.getenv("CONDUCTIVE_ADDITIVE"), os.getenv("BINDER"), os.getenv("SOLVENT")), start=1): #enumerate = numbering
    print(f"[hot_pink]Step {i}:[/hot_pink] {process}")
logger.success("Mixing complete")
print()

def coating(slurry, foil_type, coating_thickness):
	process = [ f"load the {slurry} into the coating machine",
	f"set the coating thickness to {coating_thickness}",
	"apply the slurry to the foil"]

	return process


print("[bold hot_pink]--- Coating ---[/bold hot_pink]")
logger.info("Started coating")
for i, process in enumerate(coating(os.getenv("SLURRY"), os.getenv("FOIL_TYPE"), os.getenv("COATING_THICKNESS")), start=1):
    print(f"[hot_pink]Step {i}:[/hot_pink] {process}")
logger.success("Coating complete")
print()

def calendering(coated_electrode, roller_gap, target_density):
	process = [ f"load the {coated_electrode} into the calendering roller",
	f"set the roller gap to {roller_gap}",
	f"pass the electrode through the rollers under pressure to compress it to {target_density}" ]

	return process


print("[bold hot_pink]--- Calendering ---[/bold hot_pink]")
logger.info("Started calendering")
for i,process in enumerate(calendering(os.getenv("COATED_ELECTRODE"), os.getenv("ROLLER_GAP"), os.getenv("TARGET_DENSITY")),start=1):
    print(f"[hot_pink]Step {i}:[/hot_pink] {process}")
logger.success("Calendering complete")
print()

def assemblying(cell, casing_type, electrolyte):
	process = [f"attach current collector tabs to the {cell}",
        f"place the {cell} into the {casing_type} casing",
        f"fill the casing with {electrolyte}",
        "seal the casing" ]

	return process


print("[bold hot_pink]--- Assemblying ---[/bold hot_pink]")
logger.info("Started assemblying")
for i, process in enumerate(assemblying(os.getenv("CELL"), os.getenv("CASING_TYPE"), os.getenv("ELECTROLYTE")), start=1):
    print(f"[hot_pink]Step {i}:[/hot_pink] {process}")
logger.success("Assemblying complete")
print()


print("[bold hot_pink]--- Rest ---[/bold hot_pink]")
logger.info("Started resting")
for i in tqdm(range(600), colour="magenta"): #runs 60 times
    time.sleep(0.1) #pauses for 0.1 second = 600x0.1 = 60 seconds -> bar gets updated once every 0.1 seconds
logger.success("Resting complete")
print()


logger.opt(colors=True).success("<magenta>Process complete</magenta>")
logger.info("----------------------")

notification.notify(
    title="Battery manufacturing",
    message="Process complete!",
    timeout=5
)