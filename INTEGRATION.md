# Integrating the group models

Instructions for an agent working in the app repo. That agent has not seen the repo where these models were fit. Do the backend work only. Do not edit `cluster_model.py` or `assignment_rules.py`. Do not change the frontend. Do not add scikit-learn or pandas. The saved centroids are plain numbers.

## 1. What these two files do

`cluster_model.py` is the fitted cluster model: it stores three centroids and `predict_cluster` returns the nearest one for a single student's four skill ratings. `assignment_rules.py` takes the whole class, asks `predict_cluster` for each student's cluster, and deals those clusters round-robin into 8 groups. The deal needs every student at once, because clusters are ordered from largest to smallest and the group count continues across clusters instead of starting again at group 1.

## 2. Files to copy

Copy these two files, unchanged, into a new `model/` folder at the app repo root, next to `backend/` and `frontend/`:

- `model/cluster_model.py`
- `model/assignment_rules.py`

Leave the fitting script and the elbow plot behind. The app never runs them. Also copy this file to `model/INTEGRATION.md`.

`assignment_rules.py` contains `from cluster_model import predict_cluster`. That import works when `model/` is on `sys.path`. It fails with `ModuleNotFoundError: No module named 'cluster_model'` if the app imports `model.assignment_rules` as a package. Do not rewrite that import. In `app.py`, add the folder to the path and import the modules as top-level names:

```python
import sys
from pathlib import Path

MODEL_DIR = Path(__file__).resolve().parent / "model"
sys.path.insert(0, str(MODEL_DIR))
from assignment_rules import assign_groups
from cluster_model import CENTROIDS
```

## 3. The two functions

`predict_cluster(skills)` takes the four ratings in this order: programming, data/stats, frontend/design, business/pitch. It returns a cluster number, `0`, `1`, or `2`.

```python
predict_cluster([5, 5, 5, 4])  # 2
```

`assign_groups(students, n_groups=8)` takes the whole class. Each student is a dict with `id` and the four skill fields `skill_programming`, `skill_data_stats`, `skill_frontend_design`, and `skill_business_pitch`. Ratings may be numbers or numeric strings. It returns a list of dicts, one per student, in the same order as the input. Each dict has `id`, `cluster`, and `group`. Groups are numbered from 1. Equal cluster sizes are ordered by cluster number, and ids are sorted as strings inside a cluster.

```python
assign_groups([
    {"id": "a1", "skill_programming": 4, "skill_data_stats": 4, "skill_frontend_design": 1, "skill_business_pitch": 1},
    {"id": "b2", "skill_programming": 5, "skill_data_stats": 5, "skill_frontend_design": 5, "skill_business_pitch": 4},
])
# [{"id": "a1", "cluster": 1, "group": 1}, {"id": "b2", "cluster": 2, "group": 2}]
```

Do not call `assignment_rules.py` as a script. Its `__main__` block reads `class_dataset.csv` from the current directory. The app does not have that file. Call `assign_groups` with rows from Postgres.

## 4. Where the data comes from

The models were fit on `class_dataset.csv`. The app reads Postgres. The schema is `class_dataset.sql`. `database/load.py` creates the tables from that file and loads `database/student_responses.csv`, `database/student_tools.csv`, and `database/student_availability.csv`. There is no `schema.sql`.

Query `student_responses` for every student. Use `netid` as the student `id`. The four skill inputs use the same column names as the CSV.

| Model input | Table | Column | Difference from the CSV |
|---|---|---|---|
| `id` | `student_responses` | `netid` | The CSV column is `netid`. The function argument must be named `id`. Pass the value unchanged. Some values are N-numbers (`N16059079`), some are emails (`yo2162@nyu.edu`), and `Ks7532` is mixed case. The schema allows all three. |
| `skill_programming` | `student_responses` | `skill_programming` | Same name. `SMALLINT` from 1 to 5. Do not scale. |
| `skill_data_stats` | `student_responses` | `skill_data_stats` | Same name. `SMALLINT` from 1 to 5. Do not scale. |
| `skill_frontend_design` | `student_responses` | `skill_frontend_design` | Same name. `SMALLINT` from 1 to 5. Do not scale. |
| `skill_business_pitch` | `student_responses` | `skill_business_pitch` | Same name. `SMALLINT` from 1 to 5. Do not scale. |

`name` is not a model input. Select `student_responses.name` as well, and use it only when building the JSON member lists.

These CSV columns are not model inputs. The database stores them differently, and the endpoint should ignore them:

- `tools` is one semicolon-separated cell in the CSV. The loader writes one row per tool into `student_tools.tool`.
- `availability` is one semicolon-separated cell in the CSV. The loader writes one row per slot into `student_availability.slot`.
- `working_style` can be the spreadsheet error `#NAME?` in the CSV (Avirul Islam). `database/load.py` stores that as `Not provided`, and `class_dataset.sql` rejects `#NAME?`. The models do not read this column.

The 23 netids and the four skill ratings in `database/student_responses.csv` match the model CSV. Loaded unchanged, the endpoint result below is the result to expect.

## 5. Backend

Add `GET /api/groups` in `app.py`. Follow the existing database routes: read through `backend/db.py`, and on a database error return JSON `{"error": ...}` with status 503. Do not change `frontend/`.

The handler reads every student from `student_responses`, builds the list `assign_groups` expects, and calls `assign_groups(students)`. Keep each student's `name` beside that result so the JSON can name the members. Read the centroids from `CENTROIDS` in `cluster_model.py`. Do not fit k-means again.

Return this JSON. Do not put a cluster number on any one person. `members` is names only. `clusters[].students` is a count, not a list of names.

```json
{
  "n_groups": 8,
  "groups": [
    {"group": 1, "members": ["Name One", "Name Two"], "cluster_counts": {"0": 2, "1": 1, "2": 0}}
  ],
  "clusters": [
    {"cluster": 0, "students": 13, "centroid": [2.923076923076923, 3.076923076923077, 2.8461538461538463, 4.0]}
  ],
  "groups_missing_a_cluster": 6
}
```

- `n_groups` is `8`.
- `groups` has one object per group, groups 1 through 8. `members` is the list of `name` values in that group. `cluster_counts` maps every cluster number to how many members of that group are in it, including zeros.
- `clusters` has one object per cluster. `students` is how many students were assigned that cluster. `centroid` is the four averages from `CENTROIDS`, in the skill order above.
- `groups_missing_a_cluster` is how many groups have a zero in `cluster_counts`.

The centroids are:

| Cluster | Students | Centroid |
|---|---|---|
| 0 | 13 | `[2.923076923076923, 3.076923076923077, 2.8461538461538463, 4.0]` |
| 1 | 5 | `[3.0, 3.6, 1.4, 1.6]` |
| 2 | 5 | `[4.2, 4.6, 4.0, 4.6]` |

## 6. Frontend

Do not add or change a page. `/` must keep serving `frontend/index.html` exactly as it does now.

A later page can render this JSON without another request shape. `n_groups` is how many groups were dealt. Each item in `groups` is one project group: `group` is its number, `members` is the names to show, and `cluster_counts` says how that group is mixed across skillset kinds. A zero means that group is missing that kind. `clusters` describes the kinds themselves: `cluster` is the kind's number, `students` is how many people are that kind, and `centroid` is the kind's average on programming, data/stats, frontend/design, and business/pitch. `groups_missing_a_cluster` is the count of groups that are missing at least one kind. The JSON never says which person belongs to which cluster.

## 7. Packaging

`Dockerfile` copies `requirements.txt`, `app.py`, `backend/`, and `frontend/` only. Add:

```dockerfile
COPY model ./model
```

`.dockerignore` does not exclude `model/`. Leave `requirements.txt` as Flask, gunicorn, and psycopg. Railway builds from this Dockerfile (`railway.toml` uses `builder = "DOCKERFILE"`). The `Procfile` and the image command stay `gunicorn` loading `app:app`. No new process is required, because `app.py` imports the model files.

## 8. Test

Start the app the same way as the deploy lab, from the app repo root. `app.py` listens on `PORT`, or on port 5000 when `PORT` is unset. Then:

```bash
curl http://localhost:5000/api/groups
```

Use the printed port if it is not 5000.

Expect HTTP 200 and 8 groups. Groups 1 through 7 have 3 members. Group 8 has 2. `groups_missing_a_cluster` is 6. The cluster counts are:

| Group | Members | Cluster 0 | Cluster 1 | Cluster 2 |
|---|---|---|---|---|
| 1 | 3 | 2 | 1 | 0 |
| 2 | 3 | 2 | 1 | 0 |
| 3 | 3 | 2 | 0 | 1 |
| 4 | 3 | 2 | 0 | 1 |
| 5 | 3 | 2 | 0 | 1 |
| 6 | 3 | 1 | 1 | 1 |
| 7 | 3 | 1 | 1 | 1 |
| 8 | 2 | 1 | 1 | 0 |

Open `/` in a browser. The page looks the same as before this change. Nothing new is on the screen.
