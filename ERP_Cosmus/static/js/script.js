$(document).ready(function(){
  // jQuery for toggle sub menus
  $('.sub-btn').click(function(){
      // Close other sub-menus
      $('.sub-menu').not($(this).next('.sub-menu')).slideUp();
      $('.dropdown').not($(this).find('.dropdown')).removeClass('rotate');

      // Toggle current sub-menu
      $(this).next('.sub-menu').slideToggle();
      $(this).find('.dropdown').toggleClass('rotate');
  });

  // jQuery for expand and collapse the sidebar
  $('.menu-btn').click(function(){
      $('.side-bar').addClass('active');
      $('.menu-btn').css("visibility", "hidden");
  });

  $('.close-btn').click(function(){
      $('.side-bar').removeClass('active');
      $('.menu-btn').css("visibility", "visible");
  });

  // Event listener for submenu item click
  $('.sub-item').click(function(){
      // Add any additional functionality you need when a submenu item is clicked
      console.log('Submenu item clicked');
  });
});

  //search in using sort option
//create color form
function openModal(modalId) {
  var modal = document.getElementById(modalId);
  modal.style.display = 'block';
}

// Function to close a modal
function closeModal(modalId) {
  var modal = document.getElementById(modalId);
  modal.style.display = 'none';
}

//add card in form 
document.addEventListener('DOMContentLoaded', function() {
  // Event listener for adding new cards
  document.getElementById('addButton').addEventListener('click', function() {
    createCard();
  });
});

function createCard() {
  var cardContainer = document.getElementById('cardContainer');
  var cardClone = document.querySelector('.card-clone');

  // Clone the card clone element
  var newCard = cardClone.cloneNode(true);

  // Display the new card
  newCard.style.display = 'block';

  // Reset input values in the new card
  newCard.querySelector('input[type="file"]').value = '';
  newCard.querySelector('input[name="PProduct_SKU_1"]').value = '';
  newCard.querySelector('select[name="PProduct_color_1"]').selectedIndex = 0;

  // Event listener for image preview
  newCard.querySelector('input[type="file"]').addEventListener('change', function(event) {
    var imgPreview = newCard.querySelector('.card-img-top');
    var file = event.target.files[0];
    var reader = new FileReader();

    reader.onload = function() {
      imgPreview.src = reader.result;
    }

    if (file) {
      reader.readAsDataURL(file);
    }
  });

  // Event listener for canceling the card
  newCard.querySelector('.cancel-btn').addEventListener('click', function(event) {
    var card = event.target.closest('.card');
    card.parentNode.removeChild(card);
  });

  cardContainer.appendChild(newCard);
}

// //create and update item form
document.addEventListener('DOMContentLoaded', function() {
  const field3Input = document.querySelector('#id_Item_Color');
  const field4Input = document.querySelector('#id_item_name');
  const colorOptions = Array.from(field3Input.options); // Convert options NodeList to Array

  // Event listener to trigger autofill when field1, field2, or field3 change
  field3Input.addEventListener('change', autofillField4);
  field4Input.addEventListener('input', autofillField4);

  // Function to autofill field4
  function autofillField4() {
    const selectedOption = colorOptions.find(option => option.value === field3Input.value);
    const colorName = selectedOption ? selectedOption.textContent : ''; // Get the text content of the selected option

    if (colorName) {
        // Only update field4Input if a color is selected
        const defvalue = field4Input.value.split('-')[0]; // Get the first part of the current value of field4Input
        const newValue = defvalue + '-' + colorName; // Combine the first part and the color name
        field4Input.value = newValue; // Update the value of field4Input
    }
}


});

