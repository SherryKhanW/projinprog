# Model integration lab walkthrough

By the end of this lab your app's backend can split the class into 8 project groups. You build two small models in a separate repo, package them as two files, and hand them to the agent working on your app with a set of written instructions.

- **Model 1, the cluster model:** group students by skillset kind, based on the four 1–5 skill ratings.
- **Model 2, the assignment rules:** take the whole class, ask Model 1 for each student's kind, and deal the kinds out round-robin into 8 groups to create groups with a diversity of skillsets.

**You need:** your deployed app repo from the deploy lab (running locally, `class_dataset.csv` inside it), and Cursor.

**Most common issues**

1. `ModuleNotFoundError: No module named 'cluster_model'` after the files move into the app. Inside the app the two files live in a `model/` folder, so the import has to change. Paste the error to the app's agent.
2. The app's agent rewrites `cluster_model.py` or `assignment_rules.py`. Stop it: "Do not edit the files in `model/`. Change the app to fit them."
3. A `KeyError` or "column does not exist" when you call the endpoint. The model was built from the CSV; your database has its own table and column names. Tell the agent: "read `schema.sql` and map the columns."
4. Your cluster numbers differ from a neighbor's (my cluster 0 is your cluster 2). Normal: the numbers are arbitrary. Compare the centroids and the counts.
5. The agent puts scikit-learn inside `cluster_model.py`, or adds it to the app. It should not: the saved centroids are plain numbers and the file needs no packages.
6. The agent starts building a page. Stop it: "Backend only. No frontend changes."

---

## Stage 0: a separate repo for the model

Models are built away from the app, then moved in.

1. Make a new GitHub project `groupmaker-model` and clone onto your computer. Copy `class_dataset.csv` into it from your app repo. Open the folder in a **new Cursor window** (keep the app's window for later).
2. In its terminal, create and activate a venv, then:

```
>> pip install pandas scikit-learn matplotlib
```

---

## Stage 1: how many kinds of student?

Prompt the agent:

> Write `fit_clusters.py`. Load `class_dataset.csv` and fit k-means on the four skill columns (`skill_programming`, `skill_data_stats`, `skill_frontend_design`, `skill_business_pitch`) for k from 1 to 6. Do not scale the columns. Print the number of students and the inertia for each k, and save an elbow plot as `elbow.png`. Plain script, not a notebook.

```
>> python fit_clusters.py
```

**Checkpoint 1**

Open `elbow.png`. Where does the curve stop dropping steeply? We decide k together as a class.

**Our k = ____**

(We skipped scaling because all four ratings are already on the same 1–5 scale. The apparel example needed it because income and discount share were on very different scales.)

---

## Stage 2: the centroids and the labels

Prompt the agent, with our k:

> Update `fit_clusters.py` to fit k-means with k = [our k]. Print each cluster's centroid (the four averages, 2 decimals) and how many students are in it. Add a `cluster` column with each student's label.

```
>> python fit_clusters.py
```

**Checkpoint 2** (if we chose k = 3; your cluster numbers may be in a different order)

Give each cluster a one- or two-word name from its row.

---

## Stage 3: package Model 1 as `cluster_model.py`

This is the file that will be handed to an app containing the information about the model fit.

Prompt the agent:

> Write `cluster_model.py`. It holds the centroids from the fit as plain numbers written into the file, and one function `predict_cluster(skills)` that takes the four ratings and returns the number of the nearest centroid. No imports: no scikit-learn, no pandas. Then check it: for every student in the CSV, `predict_cluster` must give the same label as the k-means fit. Print how many match.

**Checkpoint 3**

Open `cluster_model.py` and read it. Find the saved values and the calculation. This file is your fitted model. `fit_clusters.py` is how you got it; the app will never run that.

---

## Stage 4: Model 2, `assignment_rules.py`

The rule: allocate to teams the cluster with the most students, then the next largest, and so on. Deal that line around 8 groups like cards (group 1, 2, … 8, 1, 2, …), without starting over for each cluster.

Prompt the agent:

> Write `assignment_rules.py` with a function `assign_groups(students, n_groups=8)`. `students` is the whole class: a list where each student has an `id` and the four skill ratings. For each student, call `predict_cluster` from `cluster_model.py` to get their cluster. Then assign groups round-robin: order the clusters from most students to fewest, sort by `id` inside a cluster, and deal that list to groups 1 to `n_groups` in turn, continuing the count across clusters. Return each student's `id`, `cluster` and `group`. No pandas. When run directly, load the CSV (use `netid` as the id), run it, and print for each group how many students it has and how many from each cluster, then how many groups are missing a cluster.

```
>> python assignment_rules.py
```

**Checkpoint 4** (k = 3)

Is the assignment result "good" for our class assignment purposes? Why? Look at how many students are in your smallest cluster, what does that mean about ability to distribute skills?

---

## Stage 5: handoff to application integration agent

The agent in this window built the models. A different agent, in your app's window, will put them into the app. It has never seen this repo. It needs written instructions.

1. Give this agent read access to your app: add your app folder to this Cursor workspace (File → Add Folder to Workspace), or give the agent its full path.

2. Prompt the agent:

> Look at my app's codebase at [path to your app repo]. Do not change anything in it. Walk me through, step by step, what it takes to move `cluster_model.py` and `assignment_rules.py` into that app.

Read the walkthrough. It should mention a folder for the model files and how the app starts and is packaged.

3. Prompt the agent:

> Now write `INTEGRATION.md`: instructions for a new agent that works inside the app repo and has not seen this one. Use these sections:
> 1. **What these two files do**, in three sentences.
> 2. **Files to copy** and where they go in the app.
> 3. **The two functions**: name, inputs, output, with one small example each.
> 4. **Where the data comes from.** These models were built from a CSV. The app reads a Postgres database. Read the app's schema file and its data-loading script and write down, for each input the models need, which table and column it comes from, and anything that differs from the CSV. Use `netid` as the student `id`.
> 5. **Backend:** add `GET /api/groups`. It reads every student from the database, calls `assign_groups`, and returns JSON with `n_groups`; `groups` (each with `group`, `members` as a list of names, and `cluster_counts`); `clusters` (each with `cluster`, `students`, `centroid`); and `groups_missing_a_cluster`. Do not return any one person's cluster.
> 6. **Frontend:** nothing yet. Describe the JSON so a page can be built on it later.
> 7. **Packaging:** what must change so the model files are included when the app is deployed.
> 8. **Test:** the command to call the endpoint locally and the result to expect (group sizes and groups missing a cluster, from this repo's run).
> Do not edit the two model files to fit the app; the app adapts to them.

4. Read section 4 of your `INTEGRATION.md`. The model learned from a file but the live app will feed it rows from a database with its own table and column names. Check the mapping against your `schema.sql` yourself.

5. Do the move, following the walkthrough: in your **app repo**, create a `model/` folder and copy in `cluster_model.py`, `assignment_rules.py` and `INTEGRATION.md`.

---

## Stage 6: integrate the backend

Switch to your **app's Cursor window**. Start a new agent chat.

Prompt the agent:

> Read `model/INTEGRATION.md` and do the backend part only. Do not change the frontend. Do not edit `cluster_model.py` or `assignment_rules.py`.

Run the app the way you ran it in the deploy lab. In a second terminal, use the test command from your `INTEGRATION.md` (your port may differ):

```
>> curl http://localhost:[5050]/api/groups
```

**Checkpoint 6**

- JSON comes back with 8 groups and no error.
- Group sizes and `groups_missing_a_cluster` match Checkpoint 4.
- Open the app in your browser: the page looks exactly as it did before. Nothing new is on the screen, and nothing is broken.

Read the new code in `app.py`. Find the query that reads the students, the call to `assign_groups`, and the place the JSON is built.

```
>> git status        (.env NOT listed)
>> git add . && git commit -m "model integrated: /api/groups"
```

Do not push yet. We deploy in the next lab, once the page uses it.

---

## Answer in your own words

1. Which file is the fitted model, and which file did the fitting? Which of them is in your app?
2. The cluster model takes one student. The assignment rules take the whole class. Why can't the rules work one student at a time?
3. The models were built from a CSV, but the app feeds them from the database. What had to be written down for that to work, and who wrote it?

---

## Output

- A `groupmaker-model` repo: `fit_clusters.py`, `elbow.png`, `cluster_model.py`, `assignment_rules.py`, `INTEGRATION.md`.
- In your app repo: a `model/` folder with the two model files and the instructions, and a working `GET /api/groups`, committed, not yet deployed.
