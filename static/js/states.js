/* =========================================================
   states.js
   Populates the #state and #lga select boxes without a page
   reload, per the spec: "select boxes must fetch options'
   values dynamically using Asynchronous JavaScript."
   Data source: /static/data/states-lgas.json
   ========================================================= */

let stateData = [];

async function loadStateData() {
  const response = await fetch("/static/data/states-lgas.json");
  if (!response.ok) {
    console.error("Could not load states/LGA data:", response.status);
    return [];
  }
  return response.json();
}

function populateStateSelect(stateSelect) {
  stateData.forEach((entry) => {
    stateSelect.add(new Option(entry.state, entry.state));
  });

  // If the form was re-rendered after a failed submission, restore
  // whatever the user had already picked.
  const preselected = stateSelect.dataset.selected;
  if (preselected) {
    stateSelect.value = preselected;
  }
}

function populateLgaSelect(lgaSelect, stateName, preselectedLga) {
  lgaSelect.length = 1; // keep only the "Select Local Government" placeholder

  const match = stateData.find((entry) => entry.state === stateName);
  if (!match) return;

  match.local.forEach((lga) => {
    lgaSelect.add(new Option(lga, lga));
  });

  if (preselectedLga) {
    lgaSelect.value = preselectedLga;
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  const stateSelect = document.getElementById("state");
  const lgaSelect = document.getElementById("lga");
  if (!stateSelect || !lgaSelect) return;

  stateData = await loadStateData();
  populateStateSelect(stateSelect);

  // If a state was already selected (failed-validation re-render),
  // fill in its LGAs immediately too.
  if (stateSelect.value) {
    populateLgaSelect(stateSelect, stateSelect.value, lgaSelect.dataset.selected);
  }

  stateSelect.addEventListener("change", function () {
    populateLgaSelect(lgaSelect, this.value, null);
  });
});
