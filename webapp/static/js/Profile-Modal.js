
  document.addEventListener('DOMContentLoaded', function() {
      var userNameElements = document.querySelectorAll('.user-info .user-name');
      userNameElements.forEach(function(element) {
          element.textContent = element.textContent.replace(/\./g, ' ');
      });

      // Modal logic
      var modal = document.getElementById("profileModal");
      var img = document.querySelector(".profile-pic");
      var modalImg = document.getElementById("modalImage");
      var span = document.getElementsByClassName("close")[0];

      img.onclick = function(){
          modal.style.display = "block";
          modalImg.src = this.src;
      }

      span.onclick = function() {
          modal.style.display = "none";
      }

      window.onclick = function(event) {
          if (event.target == modal) {
              modal.style.display = "none";
          }
      }
  });
