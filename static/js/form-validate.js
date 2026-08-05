/* =========================================================
   form-validate.js
   Client-side validation for the Portal Form. Runs on submit
   so mistakes are caught before the request even goes out.
   The server (validators.py) always re-checks everything too -
   this file only improves the user's experience.
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("applicationForm");
  if (!form) return;

  form.addEventListener("submit", (event) => {
    clearClientErrors(form);
    const errors = collectValidationErrors(form);

    if (Object.keys(errors).length > 0) {
      event.preventDefault();
      showClientErrors(errors);
    }
  });
});

function collectValidationErrors(form) {
  const errors = {};

  form.querySelectorAll("input[required], select[required]").forEach((field) => {
    if (field.type === "radio") return; // handled separately below
    if (!field.value || !field.value.trim()) {
      errors[field.name] = "This field is required.";
    }
  });

  if (!form.querySelector('input[name="gender"]:checked')) {
    errors.gender = "Please select a gender.";
  }

  const emailField = form.querySelector('input[name="email"]');
  if (emailField.value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailField.value)) {
    errors.email = "Enter a valid email address.";
  }

  const jambField = form.querySelector('input[name="jamb_score"]');
  if (jambField.value && (jambField.value < 0 || jambField.value > 400)) {
    errors.jamb_score = "JAMB score must be between 0 and 400.";
  }

  const imageField = form.querySelector('input[name="image"]');
  if (imageField && imageField.files.length === 0) {
    errors.image = "Please upload a passport photograph.";
  }

  return errors;
}

function showClientErrors(errors) {
  Object.entries(errors).forEach(([fieldName, message]) => {
    const field = document.querySelector(`[name="${fieldName}"]`);
    if (!field) return;

    const container = field.closest(".form-group") || field.parentElement;
    const errorEl = document.createElement("span");
    errorEl.className = "field-error client-error";
    errorEl.textContent = message;
    container.appendChild(errorEl);
    field.classList.add("invalid");
  });
}

function clearClientErrors(form) {
  form.querySelectorAll(".client-error").forEach((el) => el.remove());
  form.querySelectorAll(".invalid").forEach((el) => el.classList.remove("invalid"));
}
