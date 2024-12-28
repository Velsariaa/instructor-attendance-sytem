document.addEventListener('DOMContentLoaded', function() {
    // Add event listener to all delete buttons
    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(button => {
      button.addEventListener('click', function() {
        // Get the ID of the row to delete
        const id = this.dataset.id;
        // Find the parent row and remove it
        this.closest('tr').remove();
      });
    });
  });