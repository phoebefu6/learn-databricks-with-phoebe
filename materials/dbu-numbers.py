"""DBU arithmetic for leader session 5. List prices: Azure Databricks Premium, East US, USD,
pay as you go, read 2026-10-03 from the public Azure retail prices API (saved in
materials/sources/). DS3 v2 = 0.75 DBU per hour for all-purpose and jobs compute (Azure
Databricks pricing page instance table); its Linux VM is $0.293 per hour (same API)."""
from decimal import Decimal, ROUND_HALF_UP
R = lambda x: Decimal(str(round(x, 6))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
DBU = {"all_purpose": 0.55, "jobs": 0.30, "serverless_sql": 0.70, "sql_pro": 0.55, "sql_classic": 0.22,
       "serverless_notebooks": 0.95, "serverless_jobs": 0.45}
NODE_DBU, NODE_VM = 0.75, 0.293
nodes = 5  # 1 driver + 4 workers, DS3 v2
for kind in ("all_purpose", "jobs"):
    dbu_hr = nodes * NODE_DBU
    cost = dbu_hr * DBU[kind] + nodes * NODE_VM
    print(f"{kind:12s} {dbu_hr:.2f} DBU/h x ${DBU[kind]:.2f} = ${dbu_hr*DBU[kind]:.4f} + VMs ${nodes*NODE_VM:.3f} = ${cost:.4f}/h")
ap = nodes * NODE_DBU * DBU["all_purpose"] + nodes * NODE_VM
jb = nodes * NODE_DBU * DBU["jobs"] + nodes * NODE_VM
print(f"same 2-hour nightly job: all-purpose ${R(2*ap)}, jobs ${R(2*jb)}; over 30 nights ${R(60*ap)} vs ${R(60*jb)}")
print(f"all-purpose cluster left on 14 idle hours overnight: ${R(14*ap)}")
print(f"serverless SQL 2X-Small, 4 DBU/h: ${4*DBU['serverless_sql']:.2f}/h, machines run in the Databricks-managed serverless plane")
print(f"DBU rate ratio all-purpose / jobs: {DBU['all_purpose']/DBU['jobs']:.2f}x")
