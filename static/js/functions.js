

$(document).on("click", ".open-buy-coin-modal-link", function () {
    var myCoinId = $(this).attr('data-id');
    var selectedCoinCard = $(this).closest('.card-list-coin');
    var selectedCoinTitle = selectedCoinCard.find('.card-coin-name-symbol').html();
    var selectedCoinIcon = selectedCoinCard.find('.card-coin-icon').html();
    var selectedCoinLatestPrice = selectedCoinCard.find('.card-coin-latest-price').html();
    var selectedCoinBidPrice = selectedCoinCard.find('.card-coin-bid-price').html();
    var selectedCoinAskPrice = selectedCoinCard.find('.card-coin-ask-price').html();
    $("#modal-buy-coin-header").html(selectedCoinTitle);
    $("#modal-buy-coin-icon").html(selectedCoinIcon);
    $("#modal-buy-coin-latest-price").html(selectedCoinLatestPrice);
    $("#modal-buy-coin-ask-price").html(selectedCoinAskPrice);
    $("#modal-buy-coin-bid-price").html(selectedCoinBidPrice);
});