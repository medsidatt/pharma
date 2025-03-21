$(function() {
    initSelect2();

    initDataTables();

});

// Function to initialize select2
function initSelect2() {
    $('.select2').select2();
}

// Function to initialize DataTables dynamically
function initDataTables() {
    // Loop through all tables that have the `data-url` attribute
    $('table[data-url]').each(function() {
        var $table = $(this);
        var url = $table.data('url');  // Get the API URL
        var columns = $table.data('columns').split(',');  // Get the columns from data-columns attribute

        // Initialize DataTable for each table
        let table = $table.DataTable({
            dom: 'Bfrtip',
            buttons: ['copy', 'csv', 'excel', 'pdf', 'print'],
            responsive: true,
            order: [[0, 'asc']],  // Default sorting by the first column
            ajax: {
                url: url,
                dataSrc: ''
            },
            columns: columns.map(function(col) {
                return {
                    data: col.trim(),
                    title: col.replace('_', ' ').toUpperCase() // Convert column name to a human-readable format
                };
            }),
        });

        console.log(table)
    });
}


