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
