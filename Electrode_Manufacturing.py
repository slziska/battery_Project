# testing update
from rich import print
from tqdm import tqdm
import time
from loguru import logger
from plyer import notification
from dotenv import load_dotenv
import os

# ── ADDED: talk to Camunda over plain HTTP ──────────────────────────
import requests

load_dotenv()

logger.add("battery_process.log")  # auto-writes to file AND terminal
logger.opt(colors=True).success("<magenta>Battery process started</magenta>")


def mixing(active_material, conductive_additive, binder, solvent):
    process = [f"weigh out {active_material}, {conductive_additive}, {binder}, and {solvent}",
               "mix the dry ingredients together",
               f"add the {solvent} and mix thoroughly"]

    return process


def coating(slurry, foil_type, coating_thickness):
    process = [f"load the {slurry} into the coating machine",
               f"set the coating thickness to {coating_thickness}",
               "apply the slurry to the foil"]

    return process


def calendering(coated_electrode, roller_gap, target_density):
    process = [f"load the {coated_electrode} into the calendering roller",
               f"set the roller gap to {roller_gap}",
               f"pass the electrode through the rollers under pressure to compress it to {target_density}"]

    return process


def assemblying(cell, casing_type, electrolyte):
    process = [f"attach current collector tabs to the {cell}",
               f"place the {cell} into the {casing_type} casing",
               f"fill the casing with {electrolyte}",
               "seal the casing"]

    return process


# ── CHANGED: each stage's "run it and print steps" logic used to sit
# at module level (so it fired the instant the script was imported/run,
# all four stages back to back). It's now wrapped in a function so it
# only runs when Camunda actually hands us that specific task — this is
# the core change that lets Camunda control WHEN each step happens,
# rather than the script deciding that on its own. Everything INSIDE
# each function (the print/logger calls) is identical to your original.

def run_mixing():
    print("[bold hot_pink]--- Mixing ---[/bold hot_pink]")
    logger.info("Started mixing")
    for i, process in enumerate(mixing(os.getenv("ACTIVE_MATERIAL"), os.getenv("CONDUCTIVE_ADDITIVE"),
                                        os.getenv("BINDER"), os.getenv("SOLVENT")), start=1):
        print(f"[hot_pink]Step {i}:[/hot_pink] {process}")
    logger.success("Mixing complete")
    print()


def run_coating():
    print("[bold hot_pink]--- Coating ---[/bold hot_pink]")
    logger.info("Started coating")
    for i, process in enumerate(coating(os.getenv("SLURRY"), os.getenv("FOIL_TYPE"),
                                         os.getenv("COATING_THICKNESS")), start=1):
        print(f"[hot_pink]Step {i}:[/hot_pink] {process}")
    logger.success("Coating complete")
    print()


def run_calendering():
    print("[bold hot_pink]--- Calendering ---[/bold hot_pink]")
    logger.info("Started calendering")
    for i, process in enumerate(calendering(os.getenv("COATED_ELECTRODE"), os.getenv("ROLLER_GAP"),
                                             os.getenv("TARGET_DENSITY")), start=1):
        print(f"[hot_pink]Step {i}:[/hot_pink] {process}")
    logger.success("Calendering complete")
    print()


def run_assemblying():
    print("[bold hot_pink]--- Assemblying ---[/bold hot_pink]")
    logger.info("Started assemblying")
    for i, process in enumerate(assemblying(os.getenv("CELL"), os.getenv("CASING_TYPE"),
                                             os.getenv("ELECTROLYTE")), start=1):
        print(f"[hot_pink]Step {i}:[/hot_pink] {process}")
    logger.success("Assemblying complete")
    print()

    # This part (the rest) was always last in your script, so it's kept
    # attached to the end of assemblying — it still runs right after,
    # just now triggered by Camunda completing the Assemblying task
    # rather than by falling through to the next line of the script.
    print("[bold hot_pink]--- Rest ---[/bold hot_pink]")
    logger.info("Started resting")
    for i in tqdm(range(600), colour="magenta"):  # runs 600 times
        time.sleep(0.1)  # 600 x 0.1s = 60 seconds total
    logger.success("Resting complete")
    print()

    logger.opt(colors=True).success("<magenta>Process complete</magenta>")
    logger.info("----------------------")

    notification.notify(
        title="Battery manufacturing",
        message="Process complete!",
        timeout=5
    )


# ── ADDED: Camunda connection settings ───────────────────────────────
# BASE_URL points at wherever Camunda's REST API is running. This never
# changes based on WHAT you're deploying, only WHERE Camunda itself is
# hosted (localhost, Docker, a server, etc.).
BASE_URL = "http://localhost:8080/engine-rest"
WORKER_ID = "python-worker-1"
AUTH = ("demo", "demo")  # CIB seven requires login even for the REST API

# ── ADDED: topic names, copied exactly from the .bpmn file's
# camunda:topic="..." attributes. These are how Camunda tells your
# worker WHICH step a given waiting task is for.
TOPICS = ["lib_nib.mixing", "lib_nib.coating", "lib_nib.calendering", "lib_nib.assemblying"]

# ── ADDED: map each BPMN task's activityId to the function that should
# run when that task comes up. activityId values also come straight
# from the .bpmn file (the id="..." on each <bpmn:serviceTask>).
ACTIVITY_HANDLERS = {
    "Task_Mixing": run_mixing,
    "Task_Coating": run_coating,
    "Task_Calendering": run_calendering,
    "Task_Assemblying": run_assemblying,
}


# ── ADDED: the actual "ask Camunda, then tell Camunda" cycle. This is
# the only genuinely new logic — your functions above don't know
# Camunda exists at all; this is what connects them to it.
def poll_once():
    # Ask Camunda: "is anything waiting for one of my topics?"
    resp = requests.post(
        f"{BASE_URL}/external-task/fetchAndLock",
        auth=AUTH,
        timeout=10,
        json={
            "workerId": WORKER_ID,
            "maxTasks": 5,
            "topics": [{"topicName": t, "lockDuration": 30000} for t in TOPICS],
        },
    )
    resp.raise_for_status()

    for task in resp.json():
        activity_id = task["activityId"]
        handler = ACTIVITY_HANDLERS.get(activity_id)

        if handler:
            handler()  # run your actual manufacturing step

        # Tell Camunda: "this task is done, move the process forward"
        complete_resp = requests.post(
            f"{BASE_URL}/external-task/{task['id']}/complete",
            auth=AUTH,
            json={"workerId": WORKER_ID, "variables": {}},
        )
        if complete_resp.status_code in (200, 204):
            print(f"Completed '{activity_id}'")
        else:
            print(f"Failed to complete {task['id']}: {complete_resp.text}")


def main():
    # ── CHANGED: this loop REPLACES the old "just run everything once"
    # behavior. Instead of executing all four stages back-to-back one
    # time, the script now runs forever, checking every 2 seconds for
    # new work, so it can serve any number of process instances over
    # time rather than just one run.
    print(f"Worker '{WORKER_ID}' started. Polling every 2s. Ctrl+C to stop.")
    while True:
        try:
            poll_once()
        except requests.exceptions.ConnectionError:
            print("Could not reach Camunda — is it running?")
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(2)


if __name__ == "__main__":
    main()