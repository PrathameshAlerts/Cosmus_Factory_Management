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
document.addEventListener('DOMContentLoaded', function() {
  // Event listener for adding new cards
  document.getElementById('addButton').addEventListener('click', function() {
      createCard();
  });

  // Event listener for canceling cards
  document.addEventListener('click', function(event) {
      if (event.target.classList.contains('cancel-btn')) {
          var card = event.target.closest('.card');
          card.parentNode.removeChild(card);
      }
  });
});

function createCard() {
  var cardContainer = document.getElementById('cardContainer');
  var cardTemplate = document.querySelector('.card-clone');
  var newCard = cardTemplate.cloneNode(true);

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

  cardContainer.appendChild(newCard);
}


