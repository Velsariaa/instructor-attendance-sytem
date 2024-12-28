function openModal(idNum, firstName, middleName, lastName, birthday, age, status, position, profilePictureUrl) {
    // Get the modal element
    var modal = document.getElementById("userModal");

    // Get the elements where user data will be displayed
    var idNumElement = modal.querySelector(".modal-id");
    var nameElement = modal.querySelector(".modal-name");
    var birthdayElement = modal.querySelector(".modal-birthday");
    var ageElement = modal.querySelector(".modal-age");
    var statusElement = modal.querySelector(".modal-status");
    var positionElement = modal.querySelector(".modal-position");
    var pictureElement = modal.querySelector(".modal-picture");

    // Set the user data in the modal
    idNumElement.textContent = idNum;
    nameElement.textContent = firstName + " " + middleName + " " + lastName;
    birthdayElement.textContent = birthday;
    ageElement.textContent = age;
    statusElement.textContent = status;
    positionElement.textContent = position;
    pictureElement.src = profilePictureUrl;

    // Show the modal
    modal.style.display = "block";
}