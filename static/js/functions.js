

$(document).on("click", ".open-buy-coin-modal-link", function () {
    var selectedCoinSymbol = $(this).attr('data-id');
    var selectedCoinCard = $(this).closest('.card-list-coin');
    var selectedCoinTitle = selectedCoinCard.find('.card-coin-name-symbol').html();
    var selectedCoinName = selectedCoinCard.find('.card-coin-name').html();
    var selectedCoinIcon = selectedCoinCard.find('.card-coin-icon').html();
    var selectedCoinLatestPrice = selectedCoinCard.find('.card-coin-latest-price').html();
    var selectedCoinBidPrice = selectedCoinCard.find('.card-coin-bid-price').html();
    var selectedCoinAskPrice = selectedCoinCard.find('.card-coin-ask-price').html();
    $("#modal-buy-coin-header").html(selectedCoinTitle);
    $("#modal-buy-coin-icon").html(selectedCoinIcon);
    $("#modal-buy-coin-latest-price").html(selectedCoinLatestPrice);
    $("#modal-buy-coin-ask-price").html(selectedCoinAskPrice);
    $("#modal-buy-coin-bid-price").html(selectedCoinBidPrice);
    $('#submit-buy-coin-symbol').val(selectedCoinSymbol);
    $('#submit-buy-coin-name').val(selectedCoinName);
    $('#submit-buy-coin-latest-price').val(selectedCoinLatestPrice);
    $('#submit-buy-coin-bid-price').val(selectedCoinBidPrice);
});

function updatePrice(){
    var bid_price = $('#modal-buy-coin-bid-price').html().split(" ").pop().replace(/,/g, "");
    var ticker = parseFloat($('#ticket-entry-number').val());
    var cash_spent = bid_price*ticker;
    var cash_spent = cash_spent.toFixed(2);
    $('#cash-spent-entry').val(cash_spent);
    $('#cash-spent-entry').focus();
    $('#ticket-entry-number').focus();
}

$(document).on("change, keyup", "#ticket-entry-number", updatePrice);



