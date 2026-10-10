(function () {
  "use strict";
  var D = JSON.parse(document.getElementById("site-data").textContent);
  var SVGNS = "http://www.w3.org/2000/svg";
  var L = {}, C = {};
  D.languages.forEach(function (l) { L[l.id] = l; });
  D.concepts.forEach(function (c) { C[c.id] = c; });

  function $(s, root) { return (root || document).querySelector(s); }
  function h(tag, attrs, kids) {
    var e = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) {
      if (k === "html") e.innerHTML = attrs[k];
      else if (k === "text") e.textContent = attrs[k];
      else if (k === "on") Object.keys(attrs.on).forEach(function (ev) { e.addEventListener(ev, attrs.on[ev]); });
      else if (attrs[k] !== null && attrs[k] !== undefined && attrs[k] !== false) e.setAttribute(k, attrs[k]);
    });
    (kids || []).forEach(function (k) { if (k !== null && k !== undefined) e.append(k instanceof Node ? k : document.createTextNode(k)); });
    return e;
  }
  function s(tag, attrs, text) {
    var e = document.createElementNS(SVGNS, tag);
    Object.keys(attrs || {}).forEach(function (k) { e.setAttribute(k, attrs[k]); });
    if (text !== undefined) e.textContent = text;
    return e;
  }
  function esc(t) { return String(t == null ? "" : t).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function num(x, d) { if (x === null || x === undefined || x === "") return ""; var v = Number(x).toFixed(d === undefined ? 2 : d); return v.replace(/^-/, "−"); }
  function pval(x) { if (x === null || x === undefined) return ""; return x < 0.001 ? "< 0.001" : num(x, x < 0.1 ? 3 : 2); }
  function lname(id) { if (id === "MUSK_INHERITED") return "widespread Muskogean words"; return (L[id] && L[id].name) || id; }
  function formHTML(f) { return '<i class="form">' + esc(f) + "</i>"; }
  function ordinal(n) { var v = n % 100; return n + (v >= 11 && v <= 13 ? "th" : ({ 1: "st", 2: "nd", 3: "rd" }[n % 10] || "th")); }
  function source(src) {
    if (!src) return "";
    var m = /^([A-Za-z]+)(\d{4})(?:\[(.*)\])?$/.exec(src);
    if (/^asjp/.test(src)) return "ASJP";
    if (!m) return src;
    if (m[1] === "Haas" && m[2] === "1937") return "Haas 1937, notebook p. " + m[3];
    return m[1] + " " + m[2] + (m[3] ? ": " + m[3] : "");
  }

  /* tooltip */
  var tip = $("#tip");
  function showTip(html, ev) {
    tip.innerHTML = html; tip.hidden = false;
    var x = ev.clientX + 14, y = ev.clientY + 14, r = tip.getBoundingClientRect();
    if (x + r.width > window.innerWidth - 8) x = ev.clientX - r.width - 14;
    if (y + r.height > window.innerHeight - 8) y = ev.clientY - r.height - 14;
    tip.style.left = Math.max(8, x) + "px"; tip.style.top = Math.max(8, y) + "px";
  }
  function hideTip() { tip.hidden = true; }
  function bindTip(node, html) {
    node.addEventListener("mousemove", function (ev) { showTip(html, ev); });
    node.addEventListener("mouseleave", hideTip);
    node.addEventListener("focus", function () { var r = node.getBoundingClientRect(); showTip(html, { clientX: r.right, clientY: r.top }); });
    node.addEventListener("blur", hideTip);
  }

  /* data helpers */
  var formsBy = {};
  D.forms.forEach(function (f) { var k = f.l + "|" + f.c; (formsBy[k] = formsBy[k] || []).push(f); });
  var compBy = {};
  D.comparisons.forEach(function (c) { compBy[c.l + "|" + c.c] = c; });
  var conceptIds = D.concepts.map(function (c) { return c.id; }).sort(function (a, b) { return a - b; });
  var timucuaConcepts = conceptIds.filter(function (c) { return formsBy["TIMUCUA|" + c]; });
  var tested = {};
  timucuaConcepts.forEach(function (c) { if (C[c].mres) tested[c] = true; });
  function testById(id) { return D.tests.filter(function (t) { return t.ID === id; })[0]; }

  /* hero disc: Timucua words along a spiral, rim to centre */
  function drawDisc() {
    var svg = $("#disc"); svg.innerHTML = "";
    var R0 = 262, k = 0.083, gapTurn = 1.6;
    var b = Math.log(1 - gapTurn * k) / (2 * Math.PI);
    var sq = Math.sqrt(1 + b * b);
    var theta = -Math.PI / 2, r = R0;
    svg.appendChild(s("circle", { class: "rim", r: R0 + k * R0 * 1.35 }));
    var groove = [];
    var words = timucuaConcepts.map(function (c) { return { c: c, f: formsBy["TIMUCUA|" + c][0].f }; });
    var g = s("g");
    svg.appendChild(g);
    words.forEach(function (w) {
      var fs = k * r;
      var t = s("text", { "font-size": fs.toFixed(2), "text-anchor": "middle", class: tested[w.c] ? "tested" : "" }, w.f);
      g.appendChild(t);
      var width = t.getComputedTextLength() || w.f.length * fs * 0.5;
      var span = width + fs * 0.75, half = span / 2, d = 0;
      while (d < half) { var step = Math.min(1.5, half - d); theta += step / (r * sq); r = R0 * Math.exp(b * (theta + Math.PI / 2)); d += step; groove.push([theta, r]); }
      var ang = Math.atan2(b * Math.sin(theta) + Math.cos(theta), b * Math.cos(theta) - Math.sin(theta)) * 180 / Math.PI;
      t.setAttribute("transform", "translate(" + (r * Math.cos(theta)).toFixed(2) + " " + (r * Math.sin(theta)).toFixed(2) + ") rotate(" + ang.toFixed(2) + ")");
      d = 0;
      while (d < half) { var st = Math.min(1.5, half - d); theta += st / (r * sq); r = R0 * Math.exp(b * (theta + Math.PI / 2)); d += st; groove.push([theta, r]); }
      var cc = C[w.c];
      t.addEventListener("click", function () { selectConcept(w.c, true); });
      bindTip(t, "<b>" + esc(cc.name) + "</b>: " + formHTML(w.f) + (tested[w.c] ? "<br>in the confirmatory test" : ""));
    });
    var path = groove.map(function (p, i) {
      var rr = p[1] * (1 - 0.018);
      return (i ? "L" : "M") + (rr * Math.cos(p[0])).toFixed(1) + " " + (rr * Math.sin(p[0])).toFixed(1);
    }).join("");
    svg.insertBefore(s("path", { class: "groove", d: path, transform: "rotate(0)" }), g);
    var logo = $(".brand-mark");
    if (logo && logo.src) svg.appendChild(s("image", { href: logo.src, x: -29, y: -46, width: 58, height: 63, "aria-hidden": "true" }));
    var f = s("text", { class: "formula", "text-anchor": "middle", y: 44 });
    f.appendChild(document.createTextNode("r = ae"));
    var sup = s("tspan", { dy: -7, "font-size": 12 }, "bθ"); f.appendChild(sup);
    svg.appendChild(f);
  }

  /* findings */
  function findings() {
    var h2 = testById("H2_MIKASUKI_SCA"), h4 = testById("H4_APALACHEE_SCA"), geo = testById("GEORGIA_HITCHITI_all_shared_SCA");
    var nsec = D.tests.filter(function (t) { return t.Status === "secondary"; }).length;
    var allNull = D.tests.filter(function (t) { return /^(H2|H3|H4|GEORGIA|descriptive|exploratory)/.test(t.ID); }).every(function (t) { return t.Verdict !== "supported" && !t.Ruleset_A; });
    var rank = 1 + D.donors.filter(function (d) { return d.score > D.donors.filter(function (x) { return x.focal; })[0].score; }).length;
    var items = [
      ["<b>No Timucua layer shows up in Mikasuki or Muscogee basic vocabulary.</b> Over the " + h2.N_Items + " testable residue concepts, Timucua ranks " + ordinal(rank) + " of " + D.donors.length + " candidate donors (z = " + num(h2.Z) + ", p = " + num(h2.P_Perm) + "). " + (allNull ? "All " + nsec + " secondary versions, across Creek, stricter and looser residue sets and two other similarity measures, agree." : ""), ""],
      ["<b>The null has limits.</b> The same design misses documented Yuchi–Creek and Natchez–Creek contact at this list size, so it rules out a large layer and leaves small-scale borrowing open.", ""],
      ["<b>Mikasuki's unusual residue is older than Florida.</b> Gatschet's 1884 Hitchiti, recorded from a speaker who left the Chattahoochee as a child, covers three of the residue words (who, tree, fire), and all three are there. Hitchiti and Timucua show no earlier Georgia-era link either (z = " + num(geo.Z) + ").", ""],
      ["<b>Apalachee, Timucua's Muskogean neighbour, shows nothing either</b> (z = " + num(h4.Z) + "), which matches Kimball's single shared word in the whole surviving lexicon, " + formHTML("holahta") + " 'chief'.", ""],
      ["<b>One lead runs the other way.</b> Timucua " + formHTML("efa") + " 'dog', " + formHTML("neha") + " 'grease' and " + formHTML("ilake") + " 'night' sit close to widespread Muskogean words. It was not pre-registered, so it is a question for specialists.", "lead"]
    ];
    var ul = $("#findings-list");
    items.forEach(function (it) { ul.appendChild(h("li", { class: it[1] || null, html: it[0] })); });
  }

  /* ranking strip */
  function drawStrip() {
    var box = $("#strip"); box.innerHTML = "";
    var W = Math.max(320, box.clientWidth), small = W < 560;
    var rows = [
      { title: "Candidate donors to the Mikasuki residue", data: D.donors, focalName: "Timucua" },
      { title: "Candidate recipients of Timucua's words", data: D.recipients, focalName: "Mikasuki" }
    ];
    var all = D.donors.concat(D.recipients).map(function (d) { return d.score; });
    var lo = Math.floor(Math.min.apply(null, all) - 0.2), hi = Math.ceil(Math.max.apply(null, all) + 0.2);
    var padL = 6, padR = small ? 10 : 24, band = small ? 118 : 122, top = 6;
    var H = top + rows.length * band + 40;
    var x = function (v) { return padL + (v - lo) / (hi - lo) * (W - padL - padR); };
    var svg = s("svg", { viewBox: "0 0 " + W + " " + H, role: "img", "aria-label": "Two dot plots of contact scores for 51 languages each; Timucua and Mikasuki sit near the middle." });
    rows.forEach(function (row, ri) {
      var y0 = top + ri * band, mid = y0 + 76;
      svg.appendChild(s("text", { class: "row-label", x: padL, y: y0 + 12 }, row.title));
      var placed = [], rad = small ? 4 : 4.6;
      var sorted = row.data.slice().sort(function (a, b) { return a.score - b.score; });
      sorted.forEach(function (d) {
        var cx = x(d.score), off = 0, tries = [0];
        for (var i = 1; i < 12; i++) { tries.push(i * (rad * 2 + 0.6)); if (i < 3) tries.push(-i * (rad * 2 + 0.6)); }
        for (var j = 0; j < tries.length; j++) {
          var ok = placed.every(function (p) { return Math.hypot(p[0] - cx, p[1] - (mid + tries[j])) > rad * 2 + 0.5; });
          if (ok) { off = tries[j]; break; }
        }
        placed.push([cx, mid + off]); d._cx = cx; d._cy = mid + off;
      });
      var focal = row.data.filter(function (d) { return d.focal; })[0];
      var rank = 1 + row.data.filter(function (d) { return d.score > focal.score; }).length;
      var top1 = sorted[sorted.length - 1];
      sorted.forEach(function (d) {
        var c = s("circle", { class: "dot" + (d.focal ? " focal" : ""), cx: d._cx.toFixed(1), cy: d._cy.toFixed(1), r: d.focal ? rad + 2.2 : rad });
        svg.appendChild(c);
      });
      // labels: the focal language and the top scorer
      var extents = [];
      [[focal, focal.name + ", " + ordinal(rank) + " of " + row.data.length], [top1, top1.name + " (no contact)"]].forEach(function (lab, li) {
        var d = lab[0], ly = y0 + 42, anchor = d._cx > W * 0.7 ? "end" : (d._cx < W * 0.25 ? "start" : "middle");
        if (li === 1 && Math.abs(top1._cx - focal._cx) < 30) return;
        var tw = lab[1].length * 6.6, x0 = anchor === "end" ? d._cx - tw : anchor === "middle" ? d._cx - tw / 2 : d._cx;
        if (extents.some(function (e) { return x0 < e[1] + 8 && x0 + tw > e[0] - 8; })) ly -= 17;
        extents.push([x0, x0 + tw]);
        var topDot = Math.min.apply(null, placed.filter(function (p) { return Math.abs(p[0] - d._cx) < 1; }).map(function (p) { return p[1]; }));
        svg.appendChild(s("line", { class: "leader", x1: d._cx, x2: d._cx, y1: ly + 5, y2: Math.min(d._cy, topDot) - (d.focal ? rad + 3 : rad + 1) }));
        svg.appendChild(s("text", { class: "callout", x: d._cx, y: ly, "text-anchor": anchor }, lab[1]));
      });
      sorted.forEach(function (d) {
        var hit = s("circle", { class: "hit", cx: d._cx.toFixed(1), cy: d._cy.toFixed(1), r: 9 });
        bindTip(hit, "<b>" + esc(d.name) + "</b><br>" + esc(d.family || "") + (d.macro ? ", " + esc(d.macro) : "") + "<br>contact score " + num(d.score) + " · z " + num(d.z));
        svg.appendChild(hit);
      });
    });
    var ay = top + rows.length * band + 4;
    var ax = s("g", { class: "axis" });
    ax.appendChild(s("line", { x1: x(lo), x2: x(hi), y1: ay, y2: ay }));
    for (var t = lo; t <= hi; t++) {
      ax.appendChild(s("line", { x1: x(t), x2: x(t), y1: ay, y2: ay + 4 }));
      ax.appendChild(s("text", { x: x(t), y: ay + 18, "text-anchor": "middle" }, String(t).replace("-", "−")));
    }
    ax.appendChild(s("line", { class: "zero", x1: x(0), x2: x(0), y1: top + 22, y2: ay }));
    ax.appendChild(s("text", { x: x(hi), y: ay + 34, "text-anchor": "end" }, "contact score: closer than expected →"));
    ax.appendChild(s("text", { x: x(lo), y: ay + 34, "text-anchor": "start" }, small ? "" : "← less close"));
    svg.setAttribute("viewBox", "0 0 " + W + " " + (H + 4));
    svg.appendChild(ax);
    box.appendChild(svg);
  }

  /* calibration bars */
  function drawBars() {
    var box = $("#calib"); box.innerHTML = "";
    var W = Math.max(300, box.clientWidth);
    var items = [
      ["CAL_KOASATI_x_ALABAMA", "Koasati and Alabama", "sister languages"],
      ["CAL_MOBILIAN_JARGON_x_CHOCTAW", "Mobilian Jargon and Choctaw", "a trade pidgin built on Choctaw"],
      ["CAL_MIKASUKI_x_CREEK", "Mikasuki and Creek", "branches of one family"],
      ["CAL_YUCHI_x_CREEK", "Yuchi and Creek", "documented contact, 33 shared concepts"],
      ["CAL_NATCHEZ_x_CREEK", "Natchez and Creek", "documented contact, 38 shared concepts"],
      ["H2_MIKASUKI_SCA", "Mikasuki residue and Timucua", "the confirmatory test, 15 concepts"],
      ["GEORGIA_HITCHITI_all_shared_SCA", "Hitchiti and Timucua", "Georgia-era check, 28 concepts"],
      ["H4_APALACHEE_SCA", "Apalachee and Timucua", "neighbours, 24 concepts"]
    ].map(function (r) { var t = testById(r[0]); return { id: r[0], label: r[1], sub: r[2], z: t.Z, p: t.P_Max, focal: !/^CAL/.test(r[0]), detected: t.Verdict === "detected" }; });
    var lo = -2, hi = 33, rowH = 50, top = 4, padR = 120;
    var x = function (v) { return (v - lo) / (hi - lo) * (W - padR); };
    var H = top + items.length * rowH + 30;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + H, role: "img", "aria-label": "Bar chart of z scores: known relatives score 18 to 31, documented light contact about 1, Timucua comparisons between -0.7 and 0.6." });
    items.forEach(function (d, i) {
      var y = top + i * rowH;
      svg.appendChild(s("text", { class: "bar-label", x: 0, y: y + 13 }, d.label));
      svg.appendChild(s("text", { class: "bar-sub", x: 0, y: y + 27 }, d.sub));
      var x0 = x(Math.min(0, d.z)), w = Math.max(2, Math.abs(x(d.z) - x(0)));
      var bar = s("rect", { class: "bar" + (d.focal ? " focal" : ""), x: x0, y: y + 33, width: w, height: 9, rx: 2 });
      svg.appendChild(bar);
      var vx = Math.max(x(d.z), x(0)) + 6;
      svg.appendChild(s("text", { class: "bar-value", x: vx, y: y + 41.5 }, "z " + num(d.z, 1) + (d.detected ? ", detected" : ", not detected")));
      var hit = s("rect", { class: "hit", x: 0, y: y, width: W, height: rowH - 2 });
      bindTip(hit, "<b>" + esc(d.label) + "</b><br>" + esc(d.sub) + "<br>z " + num(d.z) + ", p_max " + num(d.p, 3));
      svg.appendChild(hit);
    });
    var ay = top + items.length * rowH + 2;
    items.forEach(function (d, i) { var y = top + i * rowH; svg.appendChild(s("line", { class: "zero", x1: x(0), x2: x(0), y1: y + 31, y2: y + 45 })); });
    var ax = s("g", { class: "axis" });
    [0, 10, 20, 30].forEach(function (t) { ax.appendChild(s("text", { x: x(t), y: ay + 16, "text-anchor": "middle" }, String(t))); });
    svg.appendChild(ax);
    box.appendChild(svg);
  }

  /* generic sortable table */
  function table(container, cols, rows, opts) {
    opts = opts || {};
    var state = { key: opts.sort || null, dir: opts.dir || 1 };
    var wrap = typeof container === "string" ? $(container) : container;
    function render() {
      var data = rows.slice();
      if (state.key) {
        var col = cols.filter(function (c) { return c.key === state.key; })[0];
        var get = col.sortValue || function (r) { return r[col.key]; };
        data.sort(function (a, b) {
          var va = get(a), vb = get(b);
          if (va === null || va === undefined || va === "") return 1;
          if (vb === null || vb === undefined || vb === "") return -1;
          return (va > vb ? 1 : va < vb ? -1 : 0) * state.dir;
        });
      }
      var t = h("table");
      if (opts.caption) t.appendChild(h("caption", { text: opts.caption }));
      var tr = h("tr");
      cols.forEach(function (c) {
        var sortAttr = state.key === c.key ? (state.dir > 0 ? "ascending" : "descending") : (c.nosort ? null : "none");
        var th = h("th", { scope: "col", class: c.num ? "num" : null, "aria-sort": sortAttr });
        if (c.nosort) th.textContent = c.label;
        else th.appendChild(h("button", { type: "button", text: c.label, on: { click: function () { state.dir = state.key === c.key ? -state.dir : (c.desc ? -1 : 1); state.key = c.key; render(); } } }));
        tr.appendChild(th);
      });
      t.appendChild(h("thead", null, [tr]));
      var tb = h("tbody");
      data.forEach(function (r) {
        var row = h("tr", { class: opts.rowClass ? opts.rowClass(r) : null });
        cols.forEach(function (c) {
          var v = c.render ? c.render(r) : esc(r[c.key]);
          row.appendChild(h("td", { class: c.num ? "num" : null, html: v === null || v === undefined ? "" : String(v) }));
        });
        tb.appendChild(row);
      });
      t.appendChild(tb);
      wrap.innerHTML = ""; wrap.appendChild(t);
    }
    render();
  }

  /* concept explorer */
  var currentConcept = null;
  function selectConcept(cid, scroll) {
    currentConcept = cid;
    var c = C[cid]; $("#concept-search").value = c.name;
    document.querySelectorAll("#concept-chips .chip").forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.c === cid ? "true" : "false"); });
    var view = $("#concept-view"); view.innerHTML = "";
    var meta = [];
    if (c.gloss) meta.push("Concepticon " + c.gloss);
    if (c.stratum) meta.push(c.stratum + " vocabulary");
    if (c.wold !== null && c.wold !== undefined) meta.push("borrowed in " + Math.round(c.wold * 100) + "% of WOLD languages");
    var tags = [];
    if (c.mres) tags.push("Mikasuki residue");
    if (c.cres) tags.push("Creek residue");
    view.appendChild(h("div", { class: "concept-head" }, [h("h3", { text: "‘" + c.name + "’" }), h("span", { class: "meta", text: meta.join("; ") + (tags.length ? "; " + tags.join(", ") : "") })]));
    var letters = {}, next = 0;
    var rows = [];
    D.southeast.forEach(function (lid) {
      var fs = formsBy[lid + "|" + cid] || [];
      var comp = compBy[lid + "|" + cid];
      if (!fs.length) { rows.push({ l: lid, empty: true }); return; }
      fs.forEach(function (f, i) {
        var cog = f.cog ? (letters[f.cog] = letters[f.cog] || String.fromCharCode(65 + next++)) : "";
        rows.push({ l: lid, f: f, cog: cog, comp: comp && (comp.f === f.f || (i === 0 && !fs.some(function (x) { return x.f === comp.f; }))) ? comp : null, first: i === 0 });
      });
    });
    var wrap = h("div", { class: "table-wrap" }); view.appendChild(wrap);
    table(wrap, [
      { key: "l", label: "Language", nosort: true, render: function (r) { return r.first || r.empty ? esc(lname(r.l)) : ""; } },
      { key: "f", label: "Form", nosort: true, render: function (r) { return r.empty ? '<span class="muted">not recorded</span>' : formHTML(r.f.f); } },
      { key: "v", label: "As written", nosort: true, render: function (r) { return r.empty ? "" : '<span class="small">' + esc(r.f.v) + "</span>"; } },
      { key: "cog", label: "Set", nosort: true, render: function (r) { return r.cog ? '<span class="cog" title="automated cognate set">' + r.cog + "</span>" : ""; } },
      { key: "res", label: "Muskogean cognate", nosort: true, render: function (r) { if (r.empty || r.l === "TIMUCUA") return ""; if (r.f.res === true) return '<span class="flag">none found</span>'; if (r.f.res === false) return '<span class="small">yes</span>'; return ""; } },
      { key: "sim", label: "Closeness to Timucua", nosort: true, render: function (r) { return r.comp ? num(r.comp.sca) + ' <span class="small">rank ' + r.comp.rank + " of " + r.comp.n + ", p " + pval(r.comp.p) + "</span>" : ""; } },
      { key: "src", label: "Source", nosort: true, render: function (r) { if (r.empty) return ""; var note = r.f.note ? '<br><span class="small">' + esc(r.f.note) + "</span>" : ""; var ex = r.f.expert ? '<br><span class="small">Kimball: ' + esc(r.f.expert) + "</span>" : ""; return '<span class="small">' + esc(source(r.f.src)) + "</span>" + note + ex; } }
    ], rows, { rowClass: function (r) { return r.l === "TIMUCUA" ? "timucua" : null; } });
    if (scroll) $("#words").scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
  }
  function setupExplorer() {
    var dl = $("#concept-options");
    conceptIds.forEach(function (c) { dl.appendChild(h("option", { value: C[c].name })); });
    var input = $("#concept-search");
    function pick() {
      var v = input.value.trim().toLowerCase();
      var m = conceptIds.filter(function (c) { return C[c].name.toLowerCase() === v; })[0] || conceptIds.filter(function (c) { return C[c].name.toLowerCase().indexOf(v) === 0; })[0];
      if (m && v) selectConcept(m, false);
    }
    input.addEventListener("change", pick);
    input.addEventListener("keydown", function (e) { if (e.key === "Enter") pick(); });
    var chips = $("#concept-chips");
    ["dog", "grease", "night", "fire", "tree", "who", "flesh", "water"].forEach(function (name) {
      var c = conceptIds.filter(function (id) { return C[id].name === name; })[0];
      if (!c) return;
      chips.appendChild(h("button", { type: "button", class: "chip", "data-c": c, "aria-pressed": "false", text: name, on: { click: function () { selectConcept(c, false); } } }));
    });
    selectConcept(conceptIds.filter(function (id) { return C[id].name === "dog"; })[0], false);
  }

  /* Timucua beside each language */
  function setupBeside() {
    var langs = D.southeast.filter(function (l) { return l !== "TIMUCUA" && D.comparisons.some(function (c) { return c.l === l; }); });
    var tabs = $("#lang-tabs");
    function show(lid) {
      tabs.querySelectorAll(".tab").forEach(function (t) { t.setAttribute("aria-selected", t.dataset.l === lid ? "true" : "false"); });
      var rows = D.comparisons.filter(function (c) { return c.l === lid; }).map(function (c) {
        var fr = (formsBy[lid + "|" + c.c] || []).filter(function (f) { return f.f === c.f; })[0] || {};
        return { concept: C[c.c].name, c: c.c, f: c.f, t: c.t, sca: c.sca, rank: c.rank, n: c.n, p: c.p, res: fr.res, status: c.status };
      });
      table("#beside-table", [
        { key: "concept", label: "Concept", render: function (r) { return esc(r.concept); } },
        { key: "f", label: lname(lid), render: function (r) { return formHTML(r.f); } },
        { key: "t", label: "Timucua", render: function (r) { return formHTML(r.t); } },
        { key: "sca", label: "SCA", num: true, desc: true, render: function (r) { return num(r.sca); } },
        { key: "rank", label: "Rank of 87", num: true, render: function (r) { return r.rank; } },
        { key: "p", label: "p", num: true, render: function (r) { return pval(r.p); } },
        { key: "res", label: "Muskogean cognate", sortValue: function (r) { return r.res === true ? 0 : 1; }, render: function (r) { return r.res === true ? '<span class="flag">none found</span>' : (r.res === false ? '<span class="small">yes</span>' : ""); } },
        { key: "status", label: "Status", render: function (r) { return '<span class="small">' + esc(r.status) + "</span>"; } }
      ], rows, { sort: "p", dir: 1 });
    }
    langs.forEach(function (lid, i) {
      tabs.appendChild(h("button", { type: "button", role: "tab", class: "tab", "data-l": lid, "aria-selected": i === 0 ? "true" : "false", text: lname(lid), on: { click: function () { show(lid); } } }));
    });
    show(langs[0]);
  }

  /* tests */
  function setupTests() {
    function setName(t) {
      var id = t.ID;
      if (/strict/.test(id)) return "strict residue";
      if (/keep_european/.test(id)) return "residue incl. European-flagged words";
      if (/stratified/.test(id)) return "residue, permuted within meaning classes";
      if (/fulllist/.test(id)) return "full list";
      if (/^H2/.test(id)) return "residue";
      if (/^H3/.test(id)) return "Timucua vs widespread Muskogean words";
      if (/WARAO/.test(id)) return "full list";
      return t.Concept_Set;
    }
    function kind(t) {
      return { CONFIRMATORY: "confirmatory", secondary: "secondary", sensitivity: "sensitivity", descriptive: "descriptive", exploratory: "exploratory", H3: "H3 (direction)" }[t.Status] || t.Status;
    }
    var rows = D.tests.map(function (t) {
      return { kind: kind(t), pair: lname(t.Recipient) + " × " + lname(t.Donor), set: setName(t), n: t.N_Items, measure: t.Measure, dS: t.Delta_S, z: t.Z, p: t.P_Perm, pmax: t.P_Max, verdict: t.Verdict };
    });
    table("#tests-table", [
      { key: "kind", label: "Analysis" },
      { key: "pair", label: "Pair" },
      { key: "set", label: "Concepts", render: function (r) { var lead = parseInt(r.set, 10) || (/(\d+)/.exec(r.set) || [])[1]; var extra = !r.n ? "" : (/^\d/.test(r.set) || /same \d+/.test(r.set) ? (Number(lead) !== r.n ? " (" + r.n + " attested)" : "") : " (" + r.n + ")"); return esc(r.set) + (extra ? ' <span class="small">' + extra.trim() + "</span>" : ""); } },
      { key: "measure", label: "Measure" },
      { key: "dS", label: "ΔS", num: true, render: function (r) { return num(r.dS, 3); } },
      { key: "z", label: "z", num: true, desc: true, render: function (r) { return num(r.z); } },
      { key: "p", label: "p (perm.)", num: true, render: function (r) { return pval(r.p); } },
      { key: "pmax", label: "p_max", num: true, render: function (r) { return pval(r.pmax); } },
      { key: "verdict", label: "Verdict", render: function (r) { return '<span class="nowrap">' + (r.verdict === "detected" ? '<span class="verdict-yes">detected</span>' : esc(r.verdict === "H0 retained" ? "no signal" : r.verdict)) + "</span>"; } }
    ], rows, { rowClass: function (r) { return r.kind === "confirmatory" ? "timucua" : null; } });
  }

  /* candidates */
  function setupCandidates() {
    var groups = [
      ["Timucua -> Muskogean", "Timucua into Mikasuki and Creek"],
      ["Muskogean -> Timucua", "Muskogean into Timucua"],
      ["Timucua -> Apalachee", "Timucua and Apalachee"],
      ["Timucua -> Hitchiti", "Timucua and Hitchiti"]
    ];
    var tabs = $("#dir-tabs");
    function show(key) {
      tabs.querySelectorAll(".tab").forEach(function (t) { t.setAttribute("aria-selected", t.dataset.k === key ? "true" : "false"); });
      var rows = D.candidates.filter(function (c) { return c.Direction === key; }).map(function (c) {
        return { concept: C[String(c.c)] ? C[String(c.c)].name : c.c, rec: lname(c.Recipient), rf: c.Recipient_Form, df: c.Donor_Form, donor: lname(c.Donor), sca: c.SCA, rank: c.Rank, n: c.N, p: c.P_Candidate, bh: c.P_BH, status: c.Status };
      });
      var cols = [
        { key: "concept", label: "Concept" },
        { key: "rec", label: "Language" },
        { key: "rf", label: "Form", render: function (r) { return formHTML(r.rf); } },
        { key: "df", label: key === "Muskogean -> Timucua" ? "Muskogean match" : "Timucua", render: function (r) { return r.df ? formHTML(r.df) : ""; } },
        { key: "sca", label: "SCA", num: true, desc: true, render: function (r) { return num(r.sca); } },
        { key: "p", label: "p", num: true, render: function (r) { return pval(r.p); } }
      ];
      if (key === "Timucua -> Muskogean") cols.push({ key: "bh", label: "p after BH", num: true, render: function (r) { return pval(r.bh); } });
      table("#cand-table", cols, rows, { sort: "p", dir: 1, rowClass: function (r) { return r.p !== null && r.p <= 0.05 ? "timucua" : null; } });
    }
    groups.forEach(function (g, i) {
      tabs.appendChild(h("button", { type: "button", role: "tab", class: "tab", "data-k": g[0], "aria-selected": i === 0 ? "true" : "false", text: g[1], on: { click: function () { show(g[0]); } } }));
    });
    show(groups[0][0]);
  }

  /* places */
  function setupPlaces() {
    var sv = D.survives;
    var timucuaNames = D.places.filter(function (p) { return !/^\(/.test(p.Timucua_Period_Name); }).length;
    $("#places-lede").innerHTML = "Words can also survive as names on the map. Of " + timucuaNames + " Timucua-period province, town and river names, " + (sv.yes || 0) + " survive with good support, " + (sv.probable || 0) + " probably survive, and " + (sv.contested || 0) + " is contested. Only Arapaha, now the Alapaha River, shows the change of r to l that marks a name passed through Muskogean speakers, whose languages have no /r/. Two modern names often taken for Timucua are listed too.";
    var order = { "yes": 0, "probable": 1, "contested": 2, "no (replaced)": 3, "claimed only": 4, "": 5, "no": 6 };
    var rows = D.places.map(function (p) { return p; });
    table("#places-table", [
      { key: "Timucua_Period_Name", label: "Timucua-period name", render: function (r) { return esc(r.Timucua_Period_Name) + (r.Variants ? '<br><span class="small">' + esc(r.Variants) + "</span>" : ""); } },
      { key: "Modern_Name", label: "Modern name" },
      { key: "Survives", label: "Survives", sortValue: function (r) { return order[r.Survives] === undefined ? 9 : order[r.Survives]; }, render: function (r) { return esc(r.Survives || "n/a"); } },
      { key: "Transmission_Route", label: "How it passed", render: function (r) { return '<span class="small">' + esc(r.Transmission_Route) + "</span>"; } },
      { key: "Evidence_Grade", label: "Grade", render: function (r) { return '<span class="small">' + esc(r.Evidence_Grade) + "</span>"; } },
      { key: "Notes", label: "Notes and sources", nosort: true, render: function (r) { return '<span class="small">' + esc(r.Notes) + (r.Sources ? " " + esc(r.Sources.replace(/https?:\/\/en\.wikipedia\.org\/wiki\//g, "Wikipedia: ").replace(/_/g, " ")) : "") + "</span>"; } }
    ], rows, { sort: "Survives", dir: 1 });
  }

  /* languages */
  function setupLanguages() {
    var roleName = {
      donor_candidate: "possible donor", recipient: "tested recipient", core: "Muskogean, for cognate detection",
      reconstruction: "reconstruction (Booker 2005)", calibration: "calibration", european: "European-loan filter",
      special: "exploratory (Granberry's proposed relative)", addendum_h4: "H4 neighbour test", addendum_h1: "H1 dating test",
      source_check: "source check", control: "control panel", control_primary: "primary control"
    };
    var rate = {}; D.rates.forEach(function (r) { rate[r.id] = r; });
    var main = D.languages.filter(function (l) { return !/^control/.test(l.role); });
    table("#lang-table", [
      { key: "name", label: "Language" },
      { key: "family", label: "Family" },
      { key: "role", label: "Role here", render: function (r) { return esc(roleName[r.role] || r.role); } },
      { key: "n", label: "Forms", num: true, desc: true },
      { key: "res", label: "No Muskogean cognate", num: true, sortValue: function (r) { return rate[r.id] ? rate[r.id].rate : null; }, render: function (r) { return rate[r.id] ? Math.round(rate[r.id].rate * 100) + "%" : ""; } },
      { key: "source", label: "Source", nosort: true, render: function (r) { return '<span class="small">' + esc(r.source) + "</span>"; } }
    ], main, { rowClass: function (r) { return r.id === "TIMUCUA" ? "timucua" : null; } });
    var ctrl = D.languages.filter(function (l) { return /^control/.test(l.role); });
    table("#control-table", [
      { key: "name", label: "Language", render: function (r) { return esc(r.name) + (r.role === "control_primary" ? ' <span class="small">(primary control)</span>' : ""); } },
      { key: "family", label: "Family" },
      { key: "macroarea", label: "Region" },
      { key: "n", label: "Forms", num: true, desc: true }
    ], ctrl, { sort: "family", dir: 1 });
  }

  /* method and files */
  function setupMethod() {
    var c = D.counts;
    var stages = [
      "<b>Wordlists.</b> ASJP's 100-item lists converted to CLDF and transcribed into IPA segments, with each of four normalisation rules logged per form.",
      "<b>Inherited words.</b> LexStat and SCA cognate detection across the six Muskogean lists. A word with no cognate in another Muskogean language joins the residue: 20 Mikasuki concepts and 32 Creek.",
      "<b>European filter.</b> Residue words that match Spanish or English for the same meaning are set aside as possible recent loans.",
      "<b>Pre-registration.</b> The protocol, control panel, residue lists and code are frozen and fingerprinted before any Timucua similarity exists.",
      "<b>Similarity.</b> Every pair of words scored three ways: SCA alignment, edit distance over sound classes, and a match of the first two consonant classes.",
      "<b>The aggregate test.</b> A permutation test, then the two-way ranking against fifty stand-in donors and fifty stand-in recipients.",
      "<b>Candidates.</b> Each residue word ranked against all 87 Timucua concepts, corrected for multiple testing with Benjamini–Hochberg.",
      "<b>Addenda.</b> Apalachee (Kimball 1988) and Hitchiti (Gatschet 1884), each with its own protocol frozen before its run."
    ];
    var ol = $("#stages"); stages.forEach(function (t) { ol.appendChild(h("li", { html: t })); });
    var files = [
      ["cldf/forms.csv", c.forms.toLocaleString("en-GB") + " forms. Source spelling, normalised IPA, segments, normalisation log, and flags for Muskogean residue, the European filter and loose meaning matches."],
      ["cldf/languages.csv", c.languages + " wordlists with family, Glottocode, role in the study and data source."],
      ["cldf/parameters.csv", c.concepts + " concepts linked to Concepticon, with semantic stratum and how often each meaning is borrowed across the World Loanword Database."],
      ["cldf/cognates.csv", c.cognates.toLocaleString("en-GB") + " automated cognate judgments from the frozen run and the rerun with Hitchiti."],
      ["cldf/comparisons.csv", c.comparisons + " concept-level comparisons of each Southeastern list with Timucua: three similarity scores, rank and p-value."],
      ["cldf/tests.csv", c.tests + " aggregate tests with their statistics and verdicts."],
      ["cldf/candidates.csv", c.candidates + " candidate-loan rows from every analysis, in both directions."],
      ["cldf/place_names.csv", c.places + " place names with variants, fate, route and evidence grade."],
      ["db/project-phaistos.sqlite", "All of the above as SQLite, with views such as southeast_forms, timucua_vs_southeast and test_results."],
      ["analysis/", "The full pilot: pipeline code, pre-registration and addenda with their hashes, validation runs and every result file."]
    ];
    var dl = $("#files-list");
    files.forEach(function (f) { dl.appendChild(h("dt", { text: f[0] })); dl.appendChild(h("dd", { text: f[1] })); });
  }

  findings(); setupExplorer(); setupBeside(); setupTests(); setupCandidates(); setupPlaces(); setupLanguages(); setupMethod();
  function drawAll() { drawStrip(); drawBars(); }
  drawAll();
  drawDisc();
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { drawDisc(); drawAll(); });
  var rt; window.addEventListener("resize", function () { clearTimeout(rt); rt = setTimeout(drawAll, 150); });
})();
