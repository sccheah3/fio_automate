  
$(document).ready(function() {
    $('.searchFilter').each( function () {
        var title = $(this).text();
        $(this).html( '<input type="text" style="text-align:center; width:100px" placeholder="' + title +'" />' );
    } );
 
    // DataTable
    var table = $('#drivesTable').DataTable({
		"order": [[3, "desc"]]
	});
	$('.dataTables_length').addClass('bs-select');
 
    // Apply the search
    table.columns().every( function () {
        var that = this;
 
        $( 'input', this.footer() ).on( 'keyup change clear', function () {
            if ( that.search() !== this.value ) {
                that
                    .search( this.value )
                    .draw();
            }
        } );
    } );
} );
