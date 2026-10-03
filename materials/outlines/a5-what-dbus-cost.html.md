# a5-what-dbus-cost.html · "Leader session 5 of 6" · What a DBU costs
h1: `What a <span class="accent">DBU</span> costs` · 🟠 Hands-on · chips "Data leaders, finance partners, platform owners", "No code, one calculator"
Win: a one-page monthly estimate for your own workloads, built from list prices and DBU ratings, and the sentence "classic compute is two bills, the cloud's and Databricks'."

ALL NUMBERS from map section 5 (materials/dbu-numbers.py and its output build-alongs/dbu-numbers.out.txt). Always label: Azure Databricks Premium, East US, USD, pay as you go, read 3 October 2026; AWS and GCP differ.

Part 1 · covers what a DBU is · "A unit of processing, billed per second" · 5 min live
- Figure (a5a): a meter: a VM type is rated in DBUs per hour (DS3 v2 = 0.75 DBU/h), times hours, times the price per DBU for the workload type (all-purpose $0.55, jobs $0.30, SQL classic $0.22, SQL Pro $0.55, serverless SQL $0.70, automated serverless $0.45, interactive serverless $0.95).
- Cards: (open, Live) definitions quoted: Databricks pricing page "a normalized unit of processing power ... used for measurement and pricing purposes", per-second granularity; Azure page "A DBU is a unit of processing capability, billed on a per-second usage" and "The DBU consumption depends on the size and type of instance". (Live) the same machine has different DBU prices by workload type; Photon raises the DBU count (DS3 v2: 1.50 all-purpose Photon, 1.88 jobs Photon). (Self) where the AWS numbers stand: secondary guides report about $0.15 per DBU for jobs and $0.55 all-purpose on AWS (REPORTED); databricks.com price tables load by script and were not read.

Part 2 · covers the two bills · "Classic compute is two bills" · 6 min live
- Figure (a5b): two stacked bars for one hour of a 5-node DS3 v2 cluster: all-purpose = $2.0625 DBUs + $1.465 VMs = $3.5275; jobs = $1.125 DBUs + $1.465 VMs = $2.59. The VM part is identical; only the DBU price changes.
- Cards: (Live) Azure: "Azure Databricks bills you for virtual machines (VMs) provisioned in clusters and Databricks Units (DBUs)"; DS3 v2 Linux VM $0.293/h (Azure retail prices API). (Live) serverless runs "in the serverless compute plane, which is managed by Databricks", priced per DBU at its own rates; serverless SQL 2X-Small = 4 DBU/h = $2.80/h; warehouse sizes 4, 6, 12, 24, 40, 80, 144, 272, 528 DBU/h from 2X-Small to 4X-Large. (Self) seam: the cloud side of the bill (VM, storage, egress) in learn-aws-with-phoebe (link).

Part 3 · covers where money leaks · "Idle is the expensive part" · 5 min live
- Figure (a5c): a 24-hour strip: a 2-hour nightly job vs an all-purpose cluster left on for 14 idle hours. Numbers: nightly job $7.06 (all-purpose) vs $5.18 (jobs); 30 nights $211.65 vs $155.40; 14 idle hours on all-purpose $49.39.
- Cards: (Live) auto-termination: the classic compute best-practices page says "Enable auto termination to ensure compute is terminated after a period of inactivity"; (Live) the 1.83x rate ratio all-purpose to jobs; (Self) Free Edition: no bill, but a quota: overrun shuts compute "for the rest of the day (and in extreme cases, the rest of the month)".
- Real world (constructed): the forgotten cluster over a long weekend, computed with the same rates (say constructed; compute the number only from the hourly rate above, e.g. 72 idle hours × $3.5275 = $253.98).

Build-along (no code, one calculator): "Your monthly estimate" · figure (a5d): an estimate sheet: rows = workloads (nightly ETL job, analysts' interactive cluster, BI warehouse), columns = nodes × DBU/h × hours × $/DBU + VM $/h × nodes × hours = monthly.
Steps (each with a prompt-box showing the arithmetic): (1) list three workloads with hours per month; (2) price the nightly job on jobs compute: 5 nodes × 0.75 × 2 h × 30 = 225 DBU × $0.30 = $67.50 + VMs 5 × $0.293 × 60 h = $87.90 → $155.40 (matches map: 30 nights $155.40); (3) the same on all-purpose: 225 × $0.55 = $123.75 + $87.90 = $211.65; (4) a 2X-Small serverless SQL warehouse on for 8 hours a day, 22 days: 4 × 8 × 22 = 704 DBU × $0.70 = $492.80 (compute exactly; label as your-numbers-will-differ arithmetic, list prices); (5) write the one-line summary for finance. Bad box: "estimate = number of users × a per-seat price". Tip: re-read the price list on the day you estimate; rates and SKUs change.
Quiz: (1) why the same cluster costs $3.53 vs $2.59 (DBU price differs by workload type; VM cost same); (2) what Photon does to DBU count (raises it: DS3 v2 0.75 → 1.50 all-purpose); (3) what idle costs (14 h × $3.5275 = $49.39).
Covered: databricks.com/product/pricing (DBU definition) and Azure Databricks pricing page read at source; Azure retail prices API read 3 Oct 2026; AWS rates REPORTED; scenarios constructed.
Cheat: DBU/h × hours × $/DBU; classic = DBUs + VMs; all-purpose $0.55 vs jobs $0.30 (Azure Premium East US); 5-node DS3 v2: $3.53 vs $2.59 per hour; 2X-Small serverless SQL $2.80/h; turn idle off.
Next: session 6, lakehouse or warehouse: bring the copy map from session 1 and this estimate.
Footer: prev a4 "Notebooks versus jobs", next a6 "Lakehouse or warehouse?".
Double-check every arithmetic line yourself before writing it.
