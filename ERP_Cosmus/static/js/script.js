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
//navbar dropdown function
function showThePopUp(Subfield){
  var showPopup = document.getElementById("subfieldsContainer");
  showPopup.style.display = "block";
  showPopup.innerHTML = "<h5 class='ps-2 mt-3'>" + Subfield + "</h5>";
  
console.log(Subfield);
switch (Subfield){
  case "Main Category" :
  showPopup.innerHTML += `<ul class="mainList"><li class="pro-head"><a href="{% url 'pproductlist' %}" class="navText">Product</a></li>
  <li class="pro-head"> <a href="{% url 'item-list' %}" class="navText">Raw Material</a></li>
  <li class="pro-head"> <a href="{% url 'godown-list' %}" class="navText">Godown</a></li> </ul>`;
  break;
  case "Sub Category" :
  showPopup.innerHTML += `<ul class="mainList"><li class="pro-head"><a href="{% url 'simplecolorlistonly' %}" class="navText">Colors</a></li> 
  <li class="pro-head"><a href="{% url 'item-fabgroup-list' %}" class="navText">Fabrics Groups</a></li>
  <li class="pro-head"><a href="{% url 'unit_name-list' %}" class="navText">Units</a></li> 
  <li class="pro-head"><a href="{% url 'gst-list' %}" class="navText">GST</a></li> 
  <li class="pro-head"><a href="{% url 'fabric-finishes-list' %}" class="navText">Fabric Finshes</a></li>
  <li class="pro-head"><a href="{% url 'packaging-list' %}" class="navText">Packaging List</a></li> </ul>`;
  

  break;
  case "Product Defination":
  showPopup.innerHTML += `<ul class="mainList">
  <li class="pro-head"><a href="{% url 'define-main-category-product' %}" class="navText">Main Cat Create</a></li> 
  <li class="pro-head"><a href="{% url 'define-sub-category-product' %}" class="navText">Sub Cat Create</a></li>
  <li class="pro-head"><a href="{% url 'product-2-subcategory' %}" class="navText">Product 2 Catagory</a></li></ul>   
 `;
  break;

  case "Accounts" :
    showPopup.innerHTML +=`<ul class="mainList">
    <li class="pro-head"><a href="{% url 'account_sub_group-list' %}" class="navText">Groups</a></li> 
           <li class="pro-head"><a href="{% url 'ledger-list' %}" class="navText">Ledger</a></li>
           <li class="pro-head"><a href="{% url 'stock_item-list' %}" class="navText">Stock Item</a></li> 
    </ul>`;
    break;

  case "Vouchers":
    showPopup.innerHTML +=`<ul class="mainList">
    <li class="pro-head"> <a href="{% url 'purchase-voucher-list' %}" class="navText">Purchase Invoice</a></li> 
          <li class="pro-head"><a href="" class="navText">Sales Invoice</a></li>  
          <li class="pro-head"><a href="{% url 'stock-transfer' %}" class="navText">Stock Transfer</a></li>   
          <li class="pro-head"><a href="" class="navText">Sales Return</a></li>   
          <li class="pro-head"><a href="" class="navText">Purchase Return</a></li>   
          <li class="pro-head"><a href="" class="navText">Payment</a></li>   
          <li class="pro-head"><a href="" class="navText">Reciept</a></li>   
          <li class="pro-head"><a href="" class="navText">Journal Entry</a></li> 
    </ul>`;
    break;
  case "Reports":
    showPopup.innerHTML +=`<ul class="mainList">
           <li class="pro-head"><a href="{% url 'account_sub_group-list' %}" class="navText">Stock Transfer Report</a></li> 
           <li class="pro-head"><a href="#" class="navText">Purchase Report</a></li>
           <li class="pro-head"><a href="#" class="navText">Sales Report</a></li>   
   </ul>`;
    break;

  default:
    break;
}
 
}

//add card in form 

document.addEventListener('DOMContentLoaded', function() {
  // Counter to keep track of added cards
  var cardCounter = 1;

  // Event listener for adding new cards
  document.getElementById('addButton').addEventListener('click', function() {
    createCard();
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
    newCard.querySelector('input[name="PProduct_SKU_"]').value = '';
    newCard.querySelector('select[name="PProduct_color_"]').selectedIndex = 0;
    newCard.querySelector('input[name="Product_EANCode_"]').value = '';
   

    // Update input names with dynamic counters
    newCard.querySelectorAll('input, select').forEach(function(element) {
      var name = element.getAttribute('name');
      element.setAttribute('name', name + cardCounter);
    });

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
      cardCounter--; // Decrement the counter
  
    });

    cardContainer.appendChild(newCard);
    cardCounter++; // Increment the counter
  }

});
// //create and update item form
/*document.addEventListener('DOMContentLoaded', function() {
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
});*/
// purchase create and update item form



