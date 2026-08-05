/* =========================================================
   status-update.js
   Lets a staff member change a student's admission status
   from the Details page without a full page reload, per the
   spec: "This change of status should happen asynchronously."
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {
  const statusSelect = document.getElementById("statusSelect");
  if (!statusSelect) return;

  statusSelect.addEventListener("change", async function () {
    const studentId = this.dataset.studentId;
    const newStatus = this.value;
    const messageEl = document.getElementById("statusUpdateMessage");

    messageEl.textContent = "Saving...";
    messageEl.className = "status-update-message";

    try {
      const response = await fetch(`/students/${studentId}/status`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: newStatus })
      });

      const result = await response.json();

      if (!response.ok || !result.success) {
        throw new Error(result.error || "Could not update status.");
      }

      updateStatusDisplay(newStatus);
      messageEl.textContent = "Status updated.";
      messageEl.className = "status-update-message success";
    } catch (error) {
      messageEl.textContent = error.message;
      messageEl.className = "status-update-message error";
    }
  });
});

function updateStatusDisplay(newStatus) {
  const label = newStatus.charAt(0).toUpperCase() + newStatus.slice(1);

  const badge = document.getElementById("statusBadge");
  badge.textContent = label;
  badge.className = `status-badge status-${newStatus}`;

  const text = document.getElementById("statusText");
  text.textContent = label;

  // Re-disable whichever option is now the current status, and
  // re-enable the one that was previously selected.
  document.querySelectorAll("#statusSelect option").forEach((option) => {
    option.disabled = option.value === newStatus;
  });
  document.getElementById("statusSelect").value = "";
}
