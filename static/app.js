const cityField = document.querySelector("#city");
const localityField = document.querySelector("#locality");

cityField?.addEventListener("change", async () => {
  localityField.innerHTML = '<option value="">Loading localities…</option>';
  localityField.disabled = true;
  if (!cityField.value) {
    localityField.innerHTML = '<option value="">Choose a city first</option>';
    return;
  }
  try {
    const response = await fetch(`/api/localities/${encodeURIComponent(cityField.value)}`);
    if (!response.ok) throw new Error("Could not load localities");
    const names = await response.json();
    localityField.replaceChildren(new Option("Choose a locality", ""));
    names.forEach((name) => localityField.add(new Option(name, name)));
    localityField.disabled = names.length === 0;
  } catch {
    localityField.innerHTML = '<option value="">Could not load localities</option>';
  }
});
