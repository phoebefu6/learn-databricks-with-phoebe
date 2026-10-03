# Analyst session 6: the Unity Catalog read rule, as a local model you can run anywhere.
# A MODEL of the rule in the Databricks privileges reference, not Unity Catalog itself:
# to read a table you need USE CATALOG on its catalog, USE SCHEMA on its schema and SELECT on
# the table; a privilege granted on a catalog or schema is inherited by everything inside it.

GRANTS = set()          # (principal, privilege, securable)

def grant(priv, securable, who):
    GRANTS.add((who, priv, securable))
    kind = {1: "CATALOG", 2: "SCHEMA", 3: "TABLE"}[securable.count(".") + 1]
    print(f"GRANT {priv} ON {kind} {securable} TO `{who}`")

def has(who, priv, securable):
    parts = securable.split(".")
    # the securable itself, or any parent of it, carries the privilege (inheritance flows down)
    return any((who, priv, ".".join(parts[:i])) in GRANTS for i in range(1, len(parts) + 1))

def can_read(who, table):
    cat, sch, _ = table.split(".")
    missing = [p for p, s in (("USE CATALOG", cat), ("USE SCHEMA", f"{cat}.{sch}"), ("SELECT", table))
               if not has(who, p, s)]
    return "can read" if not missing else "denied, missing " + ", ".join(missing)

T = "main.taxi.trips"
print("1.", can_read("analysts", T))
grant("SELECT", T, "analysts")
print("2.", can_read("analysts", T))
grant("USE CATALOG", "main", "analysts")
grant("USE SCHEMA", "main.taxi", "analysts")
print("3.", can_read("analysts", T))
grant("SELECT", "main.taxi", "finance")         # schema-level SELECT: every table, now and later
grant("USE CATALOG", "main", "finance"); grant("USE SCHEMA", "main.taxi", "finance")
print("4.", can_read("finance", "main.taxi.zones_created_next_year"))
print("5.", can_read("analysts", "main.taxi.zones_created_next_year"))
