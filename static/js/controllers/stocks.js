function initDataTable() {
	var table_prefs = {
		scrollY: '70vh',
		scrollX: true,
        scrollCollapse: true,
        paging: false,
    	"order": [[ 1, "desc" ]]
	};

	$('#stocks-table').DataTable(table_prefs);
}

function initInfoTexts() {
	var infoTextIds = [
		'info-text-company',
		'info-text-debt',
		'info-text-growth-rate',
		'info-text-valuation'
	];

	for (var i = 0; i < infoTextIds.length; i++) {
		var id = infoTextIds[i];

		var title = $('#' + id + '-data span:nth-child(1)').html();
		var content = $('#' + id + '-data span:nth-child(2)').html();
		
		$('#' + id).popover({
	        html: true,
	        animation: false,
	        title: title,
	        content: content,
	        placement: 'bottom',
	        container: 'body'
	    });
	}
}

function initTableRowClickEvents() {
	$('#stocks-table tbody tr').on('click', function() {
		var chartUrl = $(this).data('chart-url');
		if (chartUrl.length > 0) {
			$('#symbol-chart-image').attr('src', '/' + chartUrl);

			var dialog = $('#chart-dialog');
			dialog.modal('show');
			dialog.on('click', function() {
				dialog.modal('hide');
			});
		}
	});
}

$(document).ready(function() {
	initDataTable();
	initInfoTexts();
	initTableRowClickEvents();
});

