document.addEventListener("DOMContentLoaded", function() {
    var path = window.location.pathname;
    var page = path.split("/").pop();
  
    if (page === "") {
      page = "main"; // Home page
    }
  
    var link = document.getElementById(page + "-link");
    if (link) {
      link.classList.add("active");
    }
  });