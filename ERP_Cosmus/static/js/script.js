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


  $('.dropdown-click').click(function(){
    console.log('Dropdown clicked');
    $('.dropdown-menu-right').not($(this).next('.dropdown-menu-right')).slideUp();
    $('.dropdown').not($(this).find('.dropdown')).removeClass('rotate');
  })

  $('.dropdown-toggle-end').click(function(){
    console.log('Dropdown clicked');
    $('.dropdown-menu-end').show();
    

  })
});




