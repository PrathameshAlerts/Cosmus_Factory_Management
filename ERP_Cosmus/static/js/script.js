$(document).ready(function(){
    //jquery for toggle sub menus
    $('.sub-btn').click(function(){
      $(this).next('.sub-menu').slideToggle();
      $(this).find('.dropdown').toggleClass('rotate');
    });

    //jquery for expand and collapse the sidebar
    $('.menu-btn').click(function(){
      $('.side-bar').addClass('active');
      $('.menu-btn').css("visibility", "hidden");
    });

    $('.close-btn').click(function(){
      $('.side-bar').removeClass('active');
      $('.menu-btn').css("visibility", "visible");
    });
  
  });

  //search in using sort option
  $(document).ready(function () {
    $('select').selectize({
        sortField: 'text'
    });
});

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
function createCard(){
  var staticCard = document.querySelector('.card-clone');
  var newCard = staticCard.cloneNode(true);
  var container = document.getElementById("cardContainer");
    container.appendChild(newCard);
  
  }
  document.getElementById("addButton").addEventListener("click", function() {
    createCard();
  });
  
  //image preview and clear
  function preview() {
    frame.src = URL.createObjectURL(event.target.files[0]);
  }
  function clearImage() {
    document.getElementById('formFile').value = null;
    frame.src = "";
  }
  //edit item

  document.addEventListener('DOMContentLoaded', function() {
    const field3Input = document.querySelector('#id_Item_Color');
    const field4Input = document.querySelector('#id_item_name');

    // Event listener to trigger autofill when field1, field2, or field3 change
    field3Input.addEventListener('input', autofillField4);
    field4Input.addEventListener('input',autofillField4);
    
    // Function to autofill field4
    function autofillField4() {
        const value3 = field3Input.value;
        const defvalue = field4Input.value; // Accessing field4Input directly
        const newValue = defvalue.split('-')[0] + '-' + value3;  // Override with new value

        field4Input.value = newValue;
    }
});