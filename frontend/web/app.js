const el = id => document.getElementById(id);
let cases = [], demo = true, configured = false, revision = 0;
const draft = {claim: "", sources: [{name:"", url:"", text:""}]};
function textNode(tag, value, className) {
  const node = document.createElement(tag);
  node.textContent = value;
  if (className) node.className = className;
  return node;
}
function invalidate() {
  revision++;
  el("result").textContent = demo ? "Select View assessment to inspect this prepared case." : "Submit your claim and passages to generate an assessment.";
  el("submit").disabled = demo ? !cases.length : !configured;
}
function syncSources() {
  const fields = [...el("sources").children];
  fields.forEach((field, i) => {
    field.querySelector("legend").textContent = "Source S" + (i + 1);
    field.querySelector(".remove").hidden = demo || fields.length === 1;
  });
  el("add").hidden = demo || fields.length >= 3;
}
function addSource(source = {}) {
  const field = el("source").content.firstElementChild.cloneNode(true);
  for (const [selector, key] of [[".name","name"],[".url","url"],[".passage","text"]]) {
    const input = field.querySelector(selector);
    input.value = source[key] || "";
    input.readOnly = demo;
  }
  field.querySelector(".urlrow").hidden = demo && !source.url;
  field.querySelector(".remove").onclick = () => { field.remove(); syncSources(); invalidate(); };
  el("sources").append(field);
  syncSources();
}
function currentInput() {
  return {claim: el("claim").value.trim(), sources: [...el("sources").children].map((f,i) => ({
    source_id: "S" + (i+1), name: f.querySelector(".name").value.trim(),
    url: f.querySelector(".url").value.trim(), text: f.querySelector(".passage").value.trim()
  }))};
}
function renderForm() {
  const selected = cases.find(c => c.id === el("case").value);
  const input = demo && selected ? selected.input : draft;
  el("demo").setAttribute("aria-pressed", String(demo));
  el("live").setAttribute("aria-pressed", String(!demo));
  el("chooser").hidden = !demo;
  el("claim").value = input.claim;
  el("claim").readOnly = demo;
  el("sources").replaceChildren();
  input.sources.forEach(addSource);
  el("submit").textContent = demo ? "View assessment" : "Verify claim";
  el("hint").textContent = demo ? "Prepared teaching example · No API key required." : configured ?
    "Your claim and passages will be sent to Gemini. Use publicly shareable text." :
    "Add GEMINI_API_KEY to the backend .env file and restart to enable live verification.";
  invalidate();
}
function showReport(report,input) {
  const area = el("result");
  area.replaceChildren(textNode("span", report.verdict, "verdict"),textNode("p", report.explanation),
    textNode("h3","Checked quotations"));
  if (!report.evidence.length) area.append(textNode("p","No supporting quotation was returned."));
  for (const evidence of report.evidence) {
    const source = input.sources.find(s => s.source_id === evidence.source_id);
    area.append(textNode("strong",source.source_id + " · " + source.name),textNode("blockquote",evidence.quote),
      textNode("p",evidence.how_it_relates));
  }
  area.append(textNode("h3","Confidence · " + report.confidence),textNode("p",report.confidence_reason));
  if (report.limitations.length) {
    const list = document.createElement("ul");
    report.limitations.forEach(l => list.append(textNode("li", l)));
    area.append(textNode("h3","Limitations"),list);
  }
  area.append(textNode("p",report.model_used));
  const button = textNode("button","Download report");
  button.onclick = () => {
    const url = URL.createObjectURL(new Blob([JSON.stringify({input,assessment:report},null,2)],{type:"application/json"}));
    const link = document.createElement("a"); link.href = url; link.download = "truthtrace-report.json"; link.click();
    setTimeout(() => URL.revokeObjectURL(url),1000);
  };
  area.append(button);
}
async function fetchJson(url, options) {
  const response = await fetch(url,options);
  const data = await response.json();
  if (!response.ok) throw new Error(Array.isArray(data.detail) ? data.detail.map(e => e.loc.slice(1).join(" ") + " · " + e.msg).join("\n") : data.detail || "Request failed.");
  return data;
}
el("demo").onclick = () => { if (!demo) Object.assign(draft,currentInput()); demo = true; renderForm(); };
el("live").onclick = () => { if (demo) {demo = false; renderForm();} };
el("case").onchange = renderForm;
el("add").onclick = () => { addSource(); invalidate(); };
el("form").oninput = invalidate;
el("form").onsubmit = async event => {
  event.preventDefault();
  const ticket = ++revision, input = currentInput();
  el("submit").disabled = true;
  el("result").textContent = "Checking evidence…";
  try {
    const report = demo ? await fetchJson("/examples/" + el("case").value + "/assessment") :
      await fetchJson("/verify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(input)});
    if (revision === ticket) showReport(report,input);
  } catch(error) { if (revision === ticket) el("result").textContent = error.message; }
  finally { if (revision === ticket) el("submit").disabled = false; }
};
async function init() {
  el("submit").disabled = true;
  try {
    const [samples,status] = await Promise.all([fetchJson("/examples"), fetchJson("/health")]);
    cases = samples; configured = status.api_key_configured;
    cases.forEach(c => el("case").add(new Option(c.title,c.id)));
    renderForm();
  } catch(error) { el("result").textContent = "Could not load the workspace. Restart the backend and refresh."; }
}
init();
