 // Get the modal
 var modal = document.getElementById("addDataModal");

 // Get the button that opens the modal
 var btn = document.getElementById("addDataBtn");

 // Get the <span> element that closes the modal
 var span = document.getElementsByClassName("close")[0];

 // When the user clicks the button, open the modal 
 btn.onclick = function() {
   modal.style.display = "block";
 }

 // When the user clicks on <span> (x), close the modal
 span.onclick = function() {
   modal.style.display = "none";
 }

 // When the user clicks anywhere outside of the modal, close it
 window.onclick = function(event) {
   if (event.target == modal) {
     modal.style.display = "none";
   }
 }

 // Preview image
 var input = document.getElementById('image');
 var preview = document.getElementById('image-preview');

 input.addEventListener('change', function() {
   var file = input.files[0];
   var reader = new FileReader();

   reader.onloadend = function() {
     preview.src = reader.result;
   }

   if (file) {
     reader.readAsDataURL(file);
   } else {
     preview.src = "";
   }
 });

 // Handle form submission via AJAX
 var form = document.getElementById('addDataForm');
 form.addEventListener('submit', function(event) {
   event.preventDefault();
   var formData = new FormData(form);
   var xhr = new XMLHttpRequest();
   xhr.open('POST', '{% url "dtrm" %}');
   xhr.setRequestHeader('X-CSRFToken', '{{ csrf_token }}');
   xhr.onload = function() {
     if (xhr.status === 200) {
       // Reload the page to display the updated data
       window.location.reload();
     } else {
       alert('An error occurred while saving data');
     }
   };
   xhr.send(formData);
 });

 