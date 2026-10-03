/* learn-databricks-with-phoebe - the Delta log bench (analyst session 8).
   Replays a real _delta_log, written by delta-rs over 8,000 real NYC TLC trips, the way
   the Delta PROTOCOL.md says a reader must: newest action per path wins, add = live file,
   remove = tombstone, latest protocol and metaData win, cdc actions are change data only.
   Then answers two questions for any version: which files are live (time travel), and
   which of them a predicate must read when per-file min/max stats are used (data skipping).
   The engine half runs in node too (module.exports) so it can be checked against Python. */
(function (root) {
  "use strict";

  /* ---------- engine ---------- */
  function cumsum(d) { var out = new Array(d.length), s = 0; for (var i = 0; i < d.length; i++) { s += d[i]; out[i] = s; } return out; }

  function load(data) {
    var m = { data: data, base: data.baseVersion, ckpt: data.checkpointVersion };
    m.pick = cumsum(data.cols.pickupMinuteDelta);
    m.pu = data.cols.puZone; m.dist = data.cols.distX100; m.fare = data.cols.fareX100;
    m.fileTrips = {};
    Object.keys(data.fileTrips).forEach(function (p) { m.fileTrips[p] = cumsum(data.fileTrips[p]); });
    m.statsCache = {};
    return m;
  }

  function versionsFor(m, branch) {
    var out = [];
    for (var v = 0; v <= m.base; v++) out.push(v);
    if (branch !== "main") Object.keys(m.data.log[branch]).map(Number).sort(function (a, b) { return a - b; }).forEach(function (v) { out.push(v); });
    return out;
  }

  function logAt(m, branch, v) {
    if (v <= m.base) return m.data.log.main[String(v)] || [];
    return (m.data.log[branch] || {})[String(v)] || [];
  }

  function applyActions(state, acts) {
    acts.forEach(function (a) {
      if (a.add) { state.live[a.add.path] = a.add; delete state.tomb[a.add.path]; }
      else if (a.remove) { delete state.live[a.remove.path]; state.tomb[a.remove.path] = a.remove; }
      else if (a.protocol) state.protocol = a.protocol;
      else if (a.metaData) state.metaData = a.metaData;
      else if (a.cdc) state.cdcSeen += 1;
    });
  }

  /* useCheckpoint: start from the checkpoint at m.ckpt when v >= m.ckpt, then read only the tail */
  function replay(m, branch, v, useCheckpoint) {
    var state = { live: {}, tomb: {}, protocol: null, metaData: null, cdcSeen: 0, commitsRead: 0, fromCheckpoint: false };
    var start = 0;
    if (useCheckpoint && v >= m.ckpt) {
      applyActions(state, m.data.checkpoint);
      state.fromCheckpoint = true;
      start = m.ckpt + 1;
    }
    for (var x = start; x <= v; x++) { applyActions(state, logAt(m, branch, x)); state.commitsRead += 1; }
    return state;
  }

  function livePaths(state) { return Object.keys(state.live).sort(); }

  function stats(m, add) {
    var s = m.statsCache[add.path];
    if (!s) { s = JSON.parse(add.stats); m.statsCache[add.path] = s; }
    return s;
  }

  function tsMinute(s) {
    var day = +s.slice(8, 10), hh = +s.slice(11, 13), mm = +s.slice(14, 16);
    return (day - 1) * 1440 + hh * 60 + mm;
  }
  function toNum(col, v) { return col === "pickup_ts" ? tsMinute(v) : v; }

  function fileMayMatch(st, conds) {
    for (var i = 0; i < conds.length; i++) {
      var c = conds[i], mn = st.minValues[c.col], mx = st.maxValues[c.col];
      if (mn === undefined || mn === null || mx === undefined || mx === null) continue;
      mn = toNum(c.col, mn); mx = toNum(c.col, mx);
      var a = toNum(c.col, c.a), ok;
      if (c.op === "=") ok = mn <= a && a <= mx;
      else if (c.op === ">") ok = mx > a;
      else if (c.op === "<") ok = mn < a;
      else ok = mx >= a && mn <= toNum(c.col, c.b);
      if (!ok) return false;
    }
    return true;
  }

  function rowValue(m, t, col) {
    var i = t - 1;
    if (col === "pickup_ts") return m.pick[i];
    if (col === "pu_zone") return m.pu[i];
    if (col === "trip_distance") return m.dist[i];
    return m.fare[i];
  }
  function rowMatches(m, t, conds) {
    for (var i = 0; i < conds.length; i++) {
      var c = conds[i], v = rowValue(m, t, c.col), a, b, ok;
      if (c.col === "trip_distance" || c.col === "fare_amount") { a = Math.round(c.a * 100); b = c.b !== undefined ? Math.round(c.b * 100) : null; }
      else { a = toNum(c.col, c.a); b = c.b !== undefined ? toNum(c.col, c.b) : null; }
      if (c.op === "=") ok = v === a;
      else if (c.op === ">") ok = v > a;
      else if (c.op === "<") ok = v < a;
      else ok = a <= v && v <= b;
      if (!ok) return false;
    }
    return true;
  }

  function mulberry32(seed) {
    var a = seed | 0;
    return function () {
      a = (a + 0x6D2B79F5) | 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  function derangement(n, seed) {
    var r = mulberry32(seed);
    for (;;) {
      var p = [], i;
      for (i = 0; i < n; i++) p.push(i);
      for (i = n - 1; i > 0; i--) { var j = Math.floor(r() * (i + 1)); var t = p[i]; p[i] = p[j]; p[j] = t; }
      if (n < 2) return p;
      var ok = true;
      for (i = 0; i < n; i++) if (p[i] === i) { ok = false; break; }
      if (ok) return p;
    }
  }

  /* the bench question: what does a predicate read at version v, and is the answer right? */
  function query(m, branch, v, conds, broken, state) {
    state = state || replay(m, branch, v, true);
    var paths = livePaths(state);
    var perm = broken ? derangement(paths.length, m.data.shuffleSeed) : null;
    var res = { files: 0, total: paths.length, bytes: 0, totalBytes: 0, rows: 0, truth: 0, perFile: [] };
    paths.forEach(function (p, i) {
      var add = state.live[p];
      var st = broken ? stats(m, state.live[paths[perm[i]]]) : stats(m, add);
      var trips = m.fileTrips[p];
      var hits = 0;
      for (var k = 0; k < trips.length; k++) if (rowMatches(m, trips[k], conds)) hits++;
      res.truth += hits;
      res.totalBytes += add.size;
      var read = fileMayMatch(st, conds);
      if (read) { res.files++; res.bytes += add.size; res.rows += hits; }
      res.perFile.push({ path: p, size: add.size, rows: trips.length, read: read, hits: hits, stats: st });
    });
    return res;
  }

  var DBX = { load: load, versionsFor: versionsFor, logAt: logAt, replay: replay, livePaths: livePaths,
              query: query, fileMayMatch: fileMayMatch, rowMatches: rowMatches, derangement: derangement,
              tsMinute: tsMinute };
  if (typeof module !== "undefined" && module.exports) module.exports = DBX;
  root.DBX = DBX;

  /* ---------- widget ---------- */
  if (typeof document === "undefined") return;

  function esc(s) { return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }
  function fmt(n) { return n.toLocaleString("en-US"); }
  function kb(b) { return (b / 1024).toFixed(1) + " KB"; }
  function pct(a, b) { return b ? (100 * a / b).toFixed(1) + "%" : "0%"; }
  var COLS = { pu_zone: "pickup zone (pu_zone)", pickup_ts: "pickup day (pickup_ts)", trip_distance: "trip_distance (miles)", fare_amount: "fare_amount (USD)" };
  var BRANCH_NAME = { zone: "Z-order by pu_zone", vendor: "Z-order by vendor_id" };

  function opLabel(acts) {
    var ci = null, adds = 0, rems = 0, cdc = 0, dc = true;
    acts.forEach(function (a) {
      if (a.commitInfo) ci = a.commitInfo;
      if (a.add) { adds++; if (a.add.dataChange === false) dc = false; }
      if (a.remove) { rems++; if (a.remove.dataChange === false) dc = false; }
      if (a.cdc) cdc++;
    });
    return { op: ci ? ci.operation : "?", params: ci ? ci.operationParameters : null, adds: adds, rems: rems, cdc: cdc, dataChange: dc };
  }

  function condText(conds) {
    return conds.map(function (c) {
      var col = c.col;
      if (col === "pickup_ts") return "pickup_ts BETWEEN '" + c.a + "' AND '" + c.b + "'";
      return col + " " + c.op + " " + c.a + (c.op === "between" ? " AND " + c.b : "");
    }).join(" AND ");
  }

  function mount(el) {
    if (!root.DBX_BENCH) { el.textContent = "Bench data did not load."; return; }
    var m = load(root.DBX_BENCH);
    var st = { branch: "zone", v: m.base, preset: "jfk", conds: root.DBX_BENCH.presets[0].conds, broken: false };

    el.innerHTML =
      '<div class="dbx-bench">' +
      '<div class="dbx-rail"><b>Real:</b> 8,000 NYC TLC yellow taxi trips from January 2024 and the <code>_delta_log</code> that delta-rs 1.6.6 wrote for them, replayed here in your browser. ' +
      '<b>Scaled:</b> files target ' + (m.data.sample.targetBytes / 1024).toFixed(0) + ' KB so 8,000 rows make several files; production files are far larger. ' +
      '<b>Constructed:</b> the re-sent 12 January batch in the MERGE.</div>' +
      '<div class="dbx-row"><span class="dbx-k">Clustering branch for v34+</span>' +
      '<button type="button" class="btn dbx-br is-on" data-br="zone">Z-order by pu_zone</button>' +
      '<button type="button" class="btn dbx-br" data-br="vendor">Z-order by vendor_id (nobody filters on it)</button></div>' +
      '<div class="dbx-row"><span class="dbx-k">Version</span><input type="range" id="dbx-ver" min="0" step="1"><b id="dbx-vlabel"></b></div>' +
      '<div id="dbx-commit" class="dbx-commit"></div>' +
      '<div class="dbx-row"><span class="dbx-k">Query</span><span id="dbx-presets"></span></div>' +
      '<div class="dbx-row dbx-own"><span class="dbx-k">Or write your own</span>' +
      '<select id="dbx-col"><option value="pu_zone">pu_zone</option><option value="pickup_ts">pickup day</option><option value="trip_distance">trip_distance</option><option value="fare_amount">fare_amount</option></select>' +
      '<select id="dbx-op"><option value="=">=</option><option value=">">&gt;</option><option value="<">&lt;</option><option value="between">between</option></select>' +
      '<input id="dbx-a" type="number" step="any" value="138" aria-label="value"><input id="dbx-b" type="number" step="any" value="" aria-label="upper value" placeholder="and">' +
      '<button type="button" class="btn" id="dbx-run">Run my predicate</button></div>' +
      '<div class="dbx-sql mono" id="dbx-sql"></div>' +
      '<div class="dbx-read" id="dbx-read"></div>' +
      '<div class="dbx-files" id="dbx-files" aria-label="live files at this version"></div>' +
      '<div class="dbx-note">Each box is one live file, wider when larger. Coral = read by the query, grey = skipped, dark red outline = skipped although it holds matching rows. The number is how many matching rows the file holds.</div>' +
      '<div class="dbx-row"><button type="button" class="btn dbx-break" id="dbx-break">Break it: shuffle the min/max stats across files</button><span class="dbx-note" id="dbx-ck"></span></div>' +
      '<div class="dbx-ladder" id="dbx-ladder"></div>' +
      "</div>";

    var $ = function (id) { return el.querySelector("#" + id); };
    var pres = $("dbx-presets");
    root.DBX_BENCH.presets.forEach(function (p) {
      var b = document.createElement("button");
      b.type = "button"; b.className = "btn dbx-pre"; b.textContent = p.label; b.setAttribute("data-pre", p.id);
      pres.appendChild(b);
    });

    function versions() { return versionsFor(m, st.branch); }
    function render() {
      var vs = versions(), maxV = vs[vs.length - 1];
      var slider = $("dbx-ver");
      slider.max = String(maxV);
      if (st.v > maxV) st.v = maxV;
      slider.value = String(st.v);
      var state = replay(m, st.branch, st.v, true);
      var full = replay(m, st.branch, st.v, false);
      var agree = livePaths(state).join("|") === livePaths(full).join("|");
      var acts = logAt(m, st.branch, st.v), o = opLabel(acts);
      $("dbx-vlabel").textContent = "v" + st.v + (st.v > m.base ? " · " + BRANCH_NAME[st.branch] + " branch" : "");
      var file = ("0000000000000000000" + st.v).slice(-20) + ".json";
      $("dbx-commit").innerHTML = '<span class="dbx-op">' + esc(o.op) + "</span> <code>_delta_log/" + file + "</code> · " +
        o.adds + " add, " + o.rems + " remove" + (o.cdc ? ", " + o.cdc + " cdc" : "") +
        " · dataChange " + (o.dataChange ? "true" : "<b>false</b> (rearranges, adds no rows)") +
        " · <b>" + livePaths(state).length + "</b> live files, " + fmt(Object.keys(state.tomb).length) + " tombstones";
      $("dbx-ck").innerHTML = state.fromCheckpoint
        ? "Snapshot built from the checkpoint at v" + m.ckpt + " plus " + (st.v - m.ckpt) + " JSON commit" + (st.v - m.ckpt === 1 ? "" : "s") + "; a replay of all " + (st.v + 1) + " commits " + (agree ? "gives the same live files ✓" : "DISAGREES ✗")
        : "Snapshot built by replaying " + (st.v + 1) + " JSON commit" + (st.v === 0 ? "" : "s") + " (no checkpoint at or before v" + st.v + ")";
      $("dbx-sql").textContent = "SELECT count(*) FROM trips VERSION AS OF " + st.v + " WHERE " + condText(st.conds);
      var r = query(m, st.branch, st.v, st.conds, st.broken, state);
      var wrong = r.rows !== r.truth;
      $("dbx-read").innerHTML =
        '<div class="dbx-num"><b>' + r.files + " of " + r.total + "</b><span>files read</span></div>" +
        '<div class="dbx-num"><b>' + pct(r.bytes, r.totalBytes) + "</b><span>of bytes read · " + kb(r.bytes) + " of " + kb(r.totalBytes) + "</span></div>" +
        '<div class="dbx-num"><b>' + fmt(r.rows) + "</b><span>rows the query returns</span></div>" +
        '<div class="dbx-num"><b>' + fmt(r.truth) + "</b><span>rows a full scan finds</span></div>" +
        '<div class="dbx-verdict ' + (wrong ? "bad" : "good") + '">' +
        (wrong ? "✗ Wrong answer: skipping trusted stats that lie and missed " + fmt(r.truth - r.rows) + " of " + fmt(r.truth) + " rows."
               : (st.broken ? "Same answer as a full scan, by luck of this layout: the shuffled stats did not hide any matching file." : "✓ Skipping is safe here: the files it skips hold none of the matching rows.")) + "</div>";
      var fz = $("dbx-files");
      fz.innerHTML = "";
      r.perFile.forEach(function (f) {
        var d = document.createElement("span");
        d.className = "dbx-f" + (f.read ? " read" : "") + (f.hits ? " has" : "");
        d.style.flexGrow = String(Math.max(1, Math.round(f.size / 1024)));
        var col = st.conds[0].col, mn = f.stats.minValues[col], mx = f.stats.maxValues[col];
        d.title = f.path.slice(0, 18) + "... " + kb(f.size) + ", " + f.rows + " rows, " + col + " min " + mn + " max " + mx + (f.read ? ", read" : ", skipped") + ", " + f.hits + " matching rows";
        d.textContent = f.hits ? String(f.hits) : "";
        fz.appendChild(d);
      });
      el.querySelectorAll(".dbx-br").forEach(function (b) { b.classList.toggle("is-on", b.getAttribute("data-br") === st.branch); });
      el.querySelectorAll(".dbx-pre").forEach(function (b) { b.classList.toggle("is-on", b.getAttribute("data-pre") === st.preset); });
      $("dbx-break").classList.toggle("is-on", st.broken);
      $("dbx-break").textContent = st.broken ? "Stats shuffled. Click to restore the honest stats" : "Break it: shuffle the min/max stats across files";
      renderLadder();
    }

    function renderLadder() {
      var rows = [["v30", "main", 30, "31 daily appends"], ["v" + m.base, "main", m.base, "after MERGE, DELETE, OPTIMIZE"],
                  ["v" + (m.base + 1) + " zone", "zone", m.base + 1, "Z-order by pu_zone"], ["v" + (m.base + 1) + " vendor", "vendor", m.base + 1, "Z-order by vendor_id"]];
      var h = '<table class="clean"><tr><th>Layout</th>';
      root.DBX_BENCH.presets.forEach(function (p) { h += "<th>" + esc(p.label) + "</th>"; });
      h += "</tr>";
      rows.forEach(function (rw) {
        var s = replay(m, rw[1], rw[2], true);
        h += "<tr><td><b>" + rw[0] + "</b> · " + rw[3] + "</td>";
        root.DBX_BENCH.presets.forEach(function (p) {
          var q = query(m, rw[1], rw[2], p.conds, st.broken, s);
          h += "<td>" + q.files + " of " + q.total + " files" + (q.rows !== q.truth ? ' <b class="dbx-bad">(' + q.rows + " of " + q.truth + " rows)</b>" : "") + "</td>";
        });
        h += "</tr>";
      });
      h += "</table><p class=\"mono\">Files read per preset query, computed live from the replayed log" + (st.broken ? ", with the stats shuffled" : "") + ".</p>";
      $("dbx-ladder").innerHTML = h;
    }

    el.addEventListener("click", function (e) {
      var t = e.target;
      if (t.classList.contains("dbx-br")) { st.branch = t.getAttribute("data-br"); render(); }
      else if (t.classList.contains("dbx-pre")) {
        var id = t.getAttribute("data-pre");
        root.DBX_BENCH.presets.forEach(function (p) { if (p.id === id) { st.conds = p.conds; st.preset = id; } });
        render();
      } else if (t.id === "dbx-break") { st.broken = !st.broken; render(); }
      else if (t.id === "dbx-run") {
        var col = $("dbx-col").value, op = $("dbx-op").value, a = parseFloat($("dbx-a").value), b = parseFloat($("dbx-b").value);
        if (isNaN(a)) return;
        var c;
        if (col === "pickup_ts") {
          var d1 = Math.min(31, Math.max(1, Math.round(a))), d2 = isNaN(b) ? d1 : Math.min(31, Math.max(1, Math.round(b)));
          if (op === "=") d2 = d1;
          if (op === ">") { d1 = d1 + 1; d2 = 31; }
          if (op === "<") { d2 = d1 - 1; d1 = 1; }
          var pad = function (n) { return (n < 10 ? "0" : "") + n; };
          c = { col: col, op: "between", a: "2024-01-" + pad(d1) + " 00:00", b: "2024-01-" + pad(Math.max(d1, d2)) + " 23:59" };
        } else if (op === "between") {
          c = { col: col, op: op, a: a, b: isNaN(b) ? a : b };
        } else c = { col: col, op: op, a: a };
        if (col === "trip_distance" || col === "fare_amount") { c.a = Math.round(c.a * 100) / 100; if (c.b !== undefined) c.b = Math.round(c.b * 100) / 100; }
        st.conds = [c]; st.preset = null; render();
      }
    });
    $("dbx-ver").addEventListener("input", function () { st.v = +this.value; render(); });
    render();
  }

  function init() { var el = document.getElementById("dbx-log-bench"); if (el) mount(el); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})(typeof window !== "undefined" ? window : this);
