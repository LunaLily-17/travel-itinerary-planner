# Travel Itinerary Planner

This Python prototype builds a single-day London itinerary using fictional attractions, admission prices and travel times. The budget covers admission only. Travel time is estimated between stops.

## Open in PyCharm or VS Code

1. Double-click the ZIP in Finder to extract it.
2. In PyCharm, use **File → Open**. In VS Code, use **File → Open Folder**.
3. Select the extracted `travel-itinerary-planner` folder that directly contains `coordinator.py`.
4. Open the editor's terminal. Run `ls` and check that it lists `coordinator.py`, `api.py`, and `agents`. In PyCharm, use **View → Tool Windows → Project** to show the file tree.

Use Python 3.10 or newer. If needed, select your Python interpreter in the editor. Run `python3 --version` in the terminal to check its version.

## Run the demo and tests

From the project folder:

```sh
python3 coordinator.py
python3 -m unittest -v test_guardrails
```

The demo should return `approved`, two visits and a £27 total admission cost. Both commands use only the Python standard library.

The tests cover a successful trip, invalid trip times, an unaffordable trip, and drafts that violate the shortlist or travel rules. Rejection tests substitute a deliberately flawed scheduler response and verify that the Coordinator withholds the itinerary.

## Run the HTTP API

```sh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m uvicorn api:app --reload
```

Open http://127.0.0.1:8000/docs, expand **POST /itineraries**, and choose **Try it out**. Submit:

```json
{
  "city": "London",
  "start_time": "09:00",
  "end_time": "16:00",
  "attraction_budget_gbp": 30,
  "interests": ["museums", "photography"]
}
```

| Request | HTTP status | Result |
|---|---|---|
| Example above | 200 | `approved` |
| End time changed to `08:00` | 422 | `invalid_request` |
| Budget changed to 0 | 200 | `no_feasible_itinerary` |
| Internal draft rejected by the Validation Agent | 500 | `validation_failed` with reasons |

Use Ctrl+C in the terminal to stop the API.

## Architecture and guardrails

| File | Responsibility |
|---|---|
| `coordinator.py` | Runs the agents in order and publishes only an approved itinerary. |
| `agents/preferences.py` | Validates and normalises trip preferences. |
| `agents/attractions.py` | Shortlists attractions by city, interests and individual admission price. |
| `agents/scheduling.py` | Proposes a route within the time and budget limits. Skips candidate routes with missing inter-stop travel times. |
| `agents/validation.py` | Checks shortlist membership, opening hours, duration, duplicates, total cost and travel gaps. Rejects missing travel estimates between distinct consecutive stops. |
| `api.py` | Exposes the Coordinator through FastAPI. |
| `test_guardrails.py` | Tests approval and rejection through the Coordinator. |

The gate follows the pattern in [CO7219 Lab 5's multi-agent example](https://github.com/ali-zahir/coX219-lab5/blob/main/agent_multi.py). The lab checks a proposed scaling action before executing it. Here, the Coordinator checks a proposed itinerary before returning it. The agents use deterministic Python rules and run in one process. Separate agent APIs and Docker deployment are outside this prototype.

## Push to a new GitHub repository

Create an empty private repository called `travel-itinerary-planner` on GitHub. Leave the README, licence and .gitignore options unchecked because this project already has its own files. The ZIP is a source snapshot, so initialise Git in the extracted project folder:

```sh
git init -b main
git add .
git status --short
git commit -m "Add travel itinerary planner with validation guardrails"
git remote add origin https://github.com/YOUR-USERNAME/travel-itinerary-planner.git
git push -u origin main
```

Replace the example URL with the HTTPS URL shown by GitHub. Check the staged file list before committing. The supplied `.gitignore` excludes the virtual environment, Python caches and local PyCharm settings.
