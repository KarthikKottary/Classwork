$(document).ready(function() {
    // Clear form
    $('#clearBtn').click(function() {
        $('#customerForm')[0].reset();
        $('#customerId').val('');
        $('#addBtn').show();
        $('#updateBtn').hide();
    });

    // Add customer
    $('#addBtn').click(function() {
        let name = $('#name').val().trim();
        let email = $('#email').val().trim();
        let phone = $('#phone').val().trim();
        let company = $('#company').val().trim();

        $.ajax({
            url: '/add',
            type: 'POST',
            data: { name, email, phone, company },
            success: function(response) {
                alert(response.message);
                if (response.status === 'success') {
                    location.reload();
                }
            },
            error: function() {
                alert('An error occurred while adding the customer.');
            }
        });
    });

    // Select customer
    $('.select-btn').click(function() {
        let id = $(this).closest('tr').data('id');
        $.ajax({
            url: '/get/' + id,
            type: 'GET',
            success: function(response) {
                if (response.status === 'error') {
                    alert(response.message);
                } else {
                    $('#customerId').val(response.id);
                    $('#name').val(response.name);
                    $('#email').val(response.email);
                    $('#phone').val(response.phone);
                    $('#company').val(response.company);
                    $('#addBtn').hide();
                    $('#updateBtn').show();
                }
            },
            error: function() {
                alert('An error occurred while fetching the customer.');
            }
        });
    });

    // Update customer
    $('#updateBtn').click(function() {
        let id = $('#customerId').val();
        let name = $('#name').val().trim();
        let email = $('#email').val().trim();
        let phone = $('#phone').val().trim();
        let company = $('#company').val().trim();

        $.ajax({
            url: '/update/' + id,
            type: 'POST',
            data: { name, email, phone, company },
            success: function(response) {
                alert(response.message);
                if (response.status === 'success') {
                    location.reload();
                }
            },
            error: function() {
                alert('An error occurred while updating the customer.');
            }
        });
    });

    // Delete customer
    $('.delete-btn').click(function() {
        let id = $(this).closest('tr').data('id');
        if (confirm('Are you sure you want to delete this customer?')) {
            $.ajax({
                url: '/delete/' + id,
                type: 'POST',
                success: function(response) {
                    alert(response.message);
                    if (response.status === 'success') {
                        location.reload();
                    }
                },
                error: function() {
                    alert('An error occurred while deleting the customer.');
                }
            });
        }
    });
});
