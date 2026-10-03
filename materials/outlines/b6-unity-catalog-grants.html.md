# b6-unity-catalog-grants.html · "Analyst session 6 of 8" · Unity Catalog grants
h1: `Unity Catalog <span class="accent">grants</span>` · 🟠 Hands-on · chips "Analysts, engineers, platform owners", "Laptop path: a local model, no account"
Script: b6.py / b6.out.txt. IMPORTANT: b6.py is a LOCAL MODEL of the documented read rule, not Unity Catalog; label it so on every output box ("Output · laptop path, local model of the documented rule (Python 3.11)") - use that label instead of the deltalake label on this page only.
Win: GRANT statements you can read and write for catalog, schema and table, a mental model of how a read is decided, and SHOW GRANTS as the way to check.

Part 1 · covers securables and privileges · "What you grant, on what" · 5 min live
- Figure (b6a): securable tree catalog main → schema main.taxi → table main.taxi.trips, with privileges that apply at each level: USE CATALOG, USE SCHEMA, SELECT, MODIFY, CREATE TABLE; plus models (CREATE MODEL, EXECUTE) and volumes (READ VOLUME, WRITE VOLUME). List of privilege types from docs.
- Cards: (open, Live) privilege types list (docs); ALL PRIVILEGES excludes EXTERNAL USE SCHEMA, EXTERNAL USE LOCATION, MANAGE, READ METADATA. (Live) GRANT syntax with the securable keyword: `GRANT SELECT ON TABLE main.taxi.trips TO \`analysts\``. (Self) seam: role design, row filters, column masks, ABAC concepts in learn-data-access-control (link); this page is Databricks' implementation.

Part 2 · covers how a read is decided · "Three checks, in order" · 6 min live
- Figure (b6b): the evaluation the local model performs: for user U reading main.taxi.trips, check USE CATALOG on main (or inherited), USE SCHEMA on main.taxi, SELECT on the table or any parent; inheritance arrows flow down. Outputs 1 to 5 from b6.out.txt.
- Cards: (Live) the documented rule quoted; inheritance to "all current and future objects". (Live) output 4: schema-level SELECT reaches main.taxi.zones_created_next_year; output 5: analysts denied, missing SELECT. (Self) what the model leaves out: ownership, MANAGE, row filters and column masks, workspace bindings, external locations.

Part 3 · covers checking grants · "Trust SHOW GRANTS, not memory" · 4 min live
- Figure (b6c): before-after: a grant matrix kept in a spreadsheet drifting from reality vs `SHOW GRANTS ON TABLE main.taxi.trips` as the source of truth; owner vs MANAGE.
- Cards: (Live) SHOW GRANTS and REVOKE as standard Unity Catalog SQL (state as standard SQL commands; do not invent output columns). (Live) MANAGE lets a non-owner manage privileges, transfer ownership, rename and drop (docs). (Self) models: CREATE MODEL + USE SCHEMA to create, EXECUTE to load (models doc), bridge to session 7.
- Real world (constructed): an analyst given SELECT on a table who still gets permission denied, debugged in three checks.

Build-along: b6.py in three parts (the model functions; grants 1 to 3; schema-level grant 4 to 5) with outputs exactly from b6.out.txt. Free Edition step (not run): on your own catalog: `GRANT USE CATALOG ON CATALOG your_catalog TO \`your_group\`;` (placeholder group name, never a guessed built-in group); `SHOW GRANTS ON SCHEMA your_catalog.your_schema;` and note that with a single user in Free Edition you can write and inspect grants but cannot watch a second person be denied, which is why the laptop model exists. Figure (b6d): the three-step decision drawn as a flowchart ending in "can read" or "denied, missing ...".
Bad box: `GRANT ALL PRIVILEGES ON CATALOG main TO \`analysts\``. Tip: grant the three read keys to a group, check with SHOW GRANTS, and revoke what inheritance gives that nobody asked for.
Quiz: (1) SELECT only on table → denied, missing USE CATALOG and USE SCHEMA; (2) schema-level SELECT reaches tables created later; (3) what the local model cannot show you.
Covered: Databricks Unity Catalog privileges reference and models-in-UC docs read at source; local model run (◐, a model); story constructed.
Cheat: GRANT priv ON CATALOG/SCHEMA/TABLE x TO `group`; three keys to read; inheritance includes future objects; ALL PRIVILEGES excludes MANAGE; SHOW GRANTS is the truth; models need EXECUTE.
Next: session 7: MLflow, where models become Unity Catalog objects governed by these same grants.
Footer: prev b5 "Data skipping, OPTIMIZE and clustering", next b7 "MLflow on Databricks".
