const input = document.querySelector("#id_telephone");
const input1 = document.querySelector("#id_phone");
const phoneInput = window.intlTelInput(input, {
  initialCountry: "auto",
  geoIpLookup: callback => {
    fetch("https://ipapi.co/json")
      .then(res => res.json())
      .then(data => callback(data.country_code))
      .catch(() => callback("ng"));
  },
  
});
const phoneInput1 = window.intlTelInput(input1, {
  initialCountry: "auto",
  geoIpLookup: callback => {
    fetch("https://ipapi.co/json")
      .then(res => res.json())
      .then(data => callback(data.country_code))
      .catch(() => callback("ng"));
  },
  
});
function addChildren() {
  // Get the input element and the list element
  const input = document.getElementById("childrenInput"); // Assuming this is the input
  const list = document.getElementById("id_children_list"); // Assuming this is the list
 
  // Get the value from the input
  const childName = input.value;

  // Check if the input is not empty
  if (childName.trim() !== "") {
      // Create a new list item with a remove button
      const listItem = document.createElement("li");
      listItem.classList.add("clists");

      const removeButton = document.createElement("button");
      removeButton.innerHTML = "<i class='fa-regular fa-trash'></i>"; // Replace 'fas fa-trash' with the desired icon class
      removeButton.classList.add("remove-button"); // Add a class to style the button
      removeButton.addEventListener("click", function () {
          list.removeChild(listItem);
          updateHiddenInput();
      });

      listItem.textContent = childName;
      listItem.appendChild(removeButton);
      list.appendChild(listItem);

      // Update the hidden input field with the current list of children
      updateHiddenInput();

      // Clear the input field
      input.value = "";
  }
}

// Function to update the hidden input field with the current list of children
function updateHiddenInput() {
  const list = document.getElementById("id_children_list"); // Assuming this is the list
  const hiddenInput = document.getElementById("id_children_info"); // Assuming this is the hidden input

  const children = [];
  list.querySelectorAll("li").forEach((child) => {
      children.push(child.textContent.trim());
  });

   // Convert the array to a comma-separated string
   const childrenString = children.map(child => `• ${child}`).join('\n');

  // Update the value of the hidden input field with the JSON stringified list of children
  hiddenInput.value = childrenString;
}
