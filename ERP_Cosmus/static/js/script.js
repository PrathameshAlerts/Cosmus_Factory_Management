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
  var staticCard = document.querySelector('.card');
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