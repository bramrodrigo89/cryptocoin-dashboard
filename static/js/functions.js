

$(document).on("click", ".open-buy-coin-modal-link", function () {
    
    var myCoinId = $(this).attr('data-id');
    var selectedCoinCard = $(this).closest('.coin-display-card');
    var selectedCoinTitle = selectedCoinCard.find('.name-symbol-coin-title').html();
    $("#buy-modal-header").val(selectedCoinTitle);
    // it is unnecessary to have to manually call the modal.
    // $('#buy-coin-modal').modal('show');
});