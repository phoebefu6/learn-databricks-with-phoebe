# a3-unity-catalog-governance.html · "Leader session 3 of 6" · Unity Catalog: who may see what
h1: `Unity Catalog: who may see <span class="accent">what</span>` · 🟡 Core · chips "Data leaders, governance owners, platform owners", "No code"
Win: a catalog layout for three teams and a grant matrix you could hand to a platform engineer, plus the rule "three keys to read: USE CATALOG, USE SCHEMA, SELECT."

Part 1 · covers the three-level namespace · "One tree for tables, volumes and models" · 5 min live
- Figure (a3a): a tree: metastore → catalogs → schemas → tables, views, volumes, models (models live in Unity Catalog as catalog.schema.model). Mechanism: every securable has exactly one parent; names are catalog.schema.object.
- Cards: (open, Live) catalog.schema.table is the full path (docs); metastore admins oversee the metastore. (Live) models in the same tree: registered models use `<catalog>.<schema>.<model>`, so the same grants govern them (models-in-UC doc). (Self) Free Edition: one workspace and one metastore per account (limitations page).
- Real world (constructed): two business units each built "customers" tables; one tree with two catalogs makes the duplicate visible.

Part 2 · covers the read rule and inheritance · "Three keys to read one table" · 6 min live
- Figure (a3b): a chain of three locks (USE CATALOG on the catalog, USE SCHEMA on the schema, SELECT on the table) and a reader who holds only SELECT stopped at the first lock; second panel: SELECT granted on a schema flows down to "all current and future objects" including a table created next year.
- Cards: (Live) the rule, quoted from the privileges reference: "SELECT on the table, USE CATALOG on the parent catalog, and USE SCHEMA on the parent schema". (Live) inheritance downwards to current and future objects; why that is powerful and why it is risky. (Self) the analyst session 6 local model's outputs: SELECT alone → denied, missing USE CATALOG, USE SCHEMA; all three → can read; schema-level SELECT reaches a table created later; another group without it → denied, missing SELECT (label: a local model of the documented rule, not Unity Catalog itself).

Part 3 · covers ownership and managing privileges · "Owners, managers and admins" · 4 min live
- Figure (a3c): before-after: left, every grant routed through one owner (bottleneck); right, owner plus a group holding MANAGE, which "allows users to manage privileges, transfer ownership, rename, and drop an object" without being the owner (docs). Note ALL PRIVILEGES excludes EXTERNAL USE SCHEMA, EXTERNAL USE LOCATION, MANAGE and READ METADATA.
- Cards: (Live) owners and MANAGE; (Live) grant to groups, not people (standard practice; say it is practice, not a quoted rule); (Self) seam: role design, row filters, column masks and ABAC concepts live in learn-data-access-control (link).
- Real world (constructed): a departing owner and the tables nobody could grant on.

Build-along (no code): "Lay out the catalog and write the grant matrix" · figure (a3d): a grid with rows = groups (analysts, finance, ml-engineers) and columns = securables (catalog prod, schema prod.sales, table prod.sales.orders, model prod.ml.churn), cells = privileges; one row filled as a constructed example.
Steps: choose the catalog split (by environment or by domain; say both are used and why); list three groups; fill the matrix with the minimum privileges; mark where inheritance gives more than intended; write each cell as the GRANT statement it becomes (`GRANT USE CATALOG ON CATALOG prod TO \`analysts\``, `GRANT USE SCHEMA ON SCHEMA prod.sales TO \`analysts\``, `GRANT SELECT ON TABLE prod.sales.orders TO \`analysts\``; for the model column say in words that loading a model needs EXECUTE on it (models-in-UC doc) and do not write a GRANT statement for models; use only the three GRANT forms shown). Bad box: "GRANT ALL PRIVILEGES ON CATALOG prod TO `everyone`". Tip: start from the read rule and add, never from ALL PRIVILEGES and subtract.
Quiz: (1) analyst with SELECT on the table only cannot read it: missing USE CATALOG and USE SCHEMA; (2) SELECT on a schema applies to tables created later; (3) MANAGE lets a non-owner manage grants.
Covered: Databricks "Unity Catalog privileges and securable objects" reference read at source; "Manage model lifecycle in Unity Catalog" read at source; local model outputs run; stories constructed.
Cheat: catalog.schema.table; three keys to read; inheritance includes future objects; MANAGE without ownership; ALL PRIVILEGES excludes MANAGE; grant to groups.
Next: session 4, notebooks versus jobs: who runs the code that reads these tables, and on what.
Footer: prev a2 "Delta: a table that remembers", next a4 "Notebooks versus jobs".
