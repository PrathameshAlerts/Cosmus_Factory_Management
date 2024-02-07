function toggleSubnav(subnavId){
    var subnav = document.getElementById(subnavId);
    if(subnav.style.display == 'block'){
        subnav.style.display = 'none';
    }else{
        subnav.style.display = 'block';
    }
}