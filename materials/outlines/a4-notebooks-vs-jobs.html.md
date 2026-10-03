# a4-notebooks-vs-jobs.html · "Leader session 4 of 6" · Notebooks versus jobs
h1: `Notebooks versus <span class="accent">jobs</span>` · 🟡 Core · chips "Data leaders, analytics and ML managers", "No code"
Win: a promote-a-notebook checklist your team uses before anything runs on a schedule, and the habit of asking "is this interactive work or automated work, and is it on the compute that matches?"

Part 1 · covers interactive and automated work · "Two kinds of work, two kinds of compute" · 5 min live
- Figure (a4a): two lanes: a person in a notebook on all-purpose (interactive) compute, attached and idle between cells; and a scheduled job on job compute that starts, runs tasks, and stops. Compute types from the docs: serverless for notebooks, serverless for jobs, classic compute, SQL warehouses.
- Cards: (open, Live) the four compute types, quoted from the compute docs; serverless "run in the serverless compute plane, which is managed by Databricks". (Live) the Azure pricing page's own wording: all-purpose for "Interactive workloads to analyze data collaboratively with notebooks", jobs for "Automated workloads to run fast and robust jobs via API or UI"; list rates $0.55 vs $0.30 per DBU-hour (Azure Premium East US, 3 Oct 2026). (Self) "For most new workloads, Databricks recommends using serverless compute" (classic compute best practices page).
- Real world (constructed): the forecast notebook that a manager scheduled from the notebook UI on an all-purpose cluster.

Part 2 · covers Lakeflow Jobs · "A job is a graph of tasks" · 5 min live
- Figure (a4b): a DAG: ingest task → two transform tasks → a model-scoring task and a dashboard-refresh task; triggers drawn as a clock (time-based) and a file arriving (event-based). Limits annotated: up to 1,000 tasks per job, 2,000 concurrent task runs per workspace, 12,000 saved jobs (docs). Free Edition: max 5 concurrent job tasks per account.
- Cards: (Live) jobs, tasks (notebook, Python script, pipeline and more), triggers (docs). (Live) Free Edition limit of 5 concurrent job tasks; enough to learn, not to run a team. (Self) seam: retries, backfills, idempotency and dependency design are orchestration concepts in learn-data-orchestration (link); this session stays with what Databricks names and charges.

Part 3 · covers what changes when code becomes a job · "From a person's notebook to a 2am run" · 5 min live
- Figure (a4c): before-after: notebook with hard-coded dates, a personal path, run by hand, results seen by one person; job with parameters, an owner, a service identity, alerts, and output to a governed table.
- Cards: (Live) parameters instead of edited cells; owner and run identity; where outputs go (a Unity Catalog table, session 3). (Live) cost: the same 5-node DS3 v2 cluster costs $3.5275/h as all-purpose and $2.59/h as jobs compute (session 5 shows the arithmetic). (Self) when a notebook should stay a notebook (exploration, one-off analysis).
- Real world: the constructed forecast notebook from Part 1, promoted.

Build-along (no code): "The promote-a-notebook checklist" · figure (a4d): a checklist card with 8 boxes grouped Inputs (parameters, data sources named by catalog.schema.table), Running (job compute or serverless jobs, owner, run identity, schedule or trigger), Outputs (governed table, alert on failure), Cost (expected DBUs from session 5).
Steps: pick a notebook someone runs by hand every week; list its inputs; decide trigger and owner; decide compute; write the checklist as a prompt-box; agree the rule "nothing scheduled from an all-purpose cluster". Bad box: "schedule the notebook as-is on the shared cluster, it works on my machine". Tip: the cheapest compute change is often moving scheduled work off interactive clusters.
Quiz: (1) which compute fits a nightly pipeline (jobs or serverless jobs); (2) Free Edition max concurrent job tasks = 5; (3) what parameters fix (hard-coded dates edited by hand).
Covered: Databricks "Compute" and "Lakeflow Jobs" docs read at source; Azure pricing page wording read at source; Free Edition limitations read at source; forecast story constructed.
Cheat: interactive vs automated; four compute types; job = DAG of tasks + trigger; limits 1,000 tasks/job, 2,000 concurrent runs/workspace; Free Edition 5 concurrent tasks; $0.55 vs $0.30 per DBU-hour (Azure Premium East US).
Next: session 5, what a DBU costs: the arithmetic behind that 0.55 versus 0.30.
Footer: prev a3 "Unity Catalog: who may see what", next a5 "What a DBU costs".
