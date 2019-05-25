$(function() {
  $('.Image-vertical, .Image-horizontal').on('click', function() {
  $('.imagepreview').attr('src', $(this).find('img').attr('src'));
  $('#imagemodal').modal('show');   
  });		
});
