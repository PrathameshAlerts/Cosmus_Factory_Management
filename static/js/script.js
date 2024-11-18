$(document).ready(function(){
   
  $('.sub-btn').click(function(){
      // Close other sub-menus
      $('.sub-menu').not($(this).next('.sub-menu')).slideUp();
      $('.dropdown').not($(this).find('.dropdown')).removeClass('rotate');
     

      // Toggle current sub-menu
      $(this).next('.sub-menu').slideToggle();
      $(this).find('.dropdown').toggleClass('rotate');
  });


  // $('.dropdown-click').click(function(){
  //   $('.dropdown-menu-right').not($(this).next('.dropdown-menu-right')).slideUp();
  //   $('.dropdown').not($(this).find('.dropdown')).removeClass('rotate');
  // })

  // $('.dropdown-toggle-end').click(function(){
  //   $('.dropdown-menu-end').show();
    

  // })
  // var firstClick = true; // Flag to track the first click

  // $('.sub-item').click(function() {
  //   console.log("First sub-item click");
    
  //   // If it's the first click, hide the text (span) and leave the image visible
  //   if (firstClick) {
  //     firstClick = false;  // Set the flag to false after the first click
      
  //     // Hide text (span) and leave only the image
  //     $('.side-bar .menu .item a').each(function() {
  //       $(this).find('span').hide();  // Hide text inside <span> tags
  //     });
      
  //     // Reduce sidebar width to only show icons
  //     $('.side-bar').css('width', '50px');
  //   } else {
  //     // On subsequent clicks, toggle between hiding and showing the text
  //     $('.side-bar .menu .item a').each(function() {
  //       $(this).find('span').toggle();  // Toggle visibility of text inside <span> tags
  //     });
      
  //     // Expand sidebar width to show both images and text
  //     $('.side-bar').css('width', '235px');
  //   }
    
  //   // Optionally, make sure to display text when the image is clicked again
  //   $('.side-bar .menu .item a img').click(function() {
  //     $('.side-bar').css('width', '235px'); // Expand sidebar back to original width
  //     $('.side-bar .menu .item a').each(function() {
  //       $(this).find('span').show(); // Show the text inside <span> tags
  //     });
  //   });
  // });
  
});





