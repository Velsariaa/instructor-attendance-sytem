window.onload = function() {
    document.getElementById("copyButton").addEventListener("click", function() {
        // Select the table rows in the Employee section
        var rows = document.querySelectorAll('#Employee table tr');

        // Select the wrapper div in the History section
        var historyWrapper = document.getElementById('historyWrapper');
        historyWrapper.innerHTML = ''; // Clear previous history

        // Create a box to hold the history content
        var box = document.createElement('div');
        box.className = 'box';

        // Iterate through each row starting from the second one (skipping the header)
        for (var i = 1; i < rows.length; i++) {
            var cells = rows[i].getElementsByTagName('td');

            // Get the username, date, profile pic, email, address, and gender from the cells
            var username = cells[4].innerHTML; // Assuming username is in the fifth column
            var date = cells[8].innerHTML; // Assuming date is in the ninth column
            var profilePic = cells[1].innerHTML; // Assuming profile pic is in the second column
            var email = cells[5].innerHTML;
            var address = cells[6].innerHTML;
            var gender = cells[7].innerHTML;

            // Construct the HTML content for the box
            box.innerHTML += '<div class="employee">' +
                                '<h2>' + username + '</h2>' +
                                '<p>Date: ' + date + '</p>' +
                                '<img src="' + profilePic + '" alt="Profile Pic" class="profile">' +
                                '<p>Email: ' + email + '</p>' +
                                '<p>Address: ' + address + '</p>' +
                                '<p>Gender: ' + gender + '</p>' +
                              '</div>';
        }

        // Append the box to the historyWrapper
        historyWrapper.appendChild(box);
    });
};
