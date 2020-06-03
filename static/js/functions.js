// Taken from "How to format a number as a currency value in JavaScript"
// https://flaviocopes.com/how-to-format-number-as-currency-javascript/

const formatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  minimumFractionDigits: 2
})

const buyButton = document.getElementById('modal-buy-button');

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

function check_cash_left(cash_spent){
    var submitBuyButton =  $('#modal-buy-button');
    var available_cash = $('#modal-cash-available').html().split(" ").pop().replace(/,/g, "");
    cash_left = available_cash - cash_spent
    if (cash_left >= 0.0) {
        buyButton.disabled = false;
        submitBuyButton.removeClass('tooltipped');
        submitBuyButton.removeAttr('data-position');
        submitBuyButton.removeAttr('data-tooltip');
        submitBuyButton.removeAttr('data-tooltip-id')
    } else {
        buyButton.disabled = true;
        submitBuyButton.addClass('tooltipped');
        submitBuyButton.attr('data-position', 'top');
        submitBuyButton.attr('data-tooltip', 'You do not have enough cash in your wallet. Add more funds to keep buying coins!');
        submitBuyButton.tooltip();
    }
}

function updatePrice(){
    var bid_price = $('#modal-buy-coin-bid-price').html().split(" ").pop().replace(/,/g, "");
    var ticker = parseFloat($('#ticket-entry-number').val());
    var cash_spent = bid_price*ticker;
    var cash_spent = cash_spent.toFixed(2);
    $('#cash-spent-entry').val(cash_spent);
    $('#cash-spent-entry').focus();
    $('#ticket-entry-number').focus();
    check_cash_left(cash_spent);
}

function updateTicker(){
    var bid_price = $('#modal-buy-coin-bid-price').html().split(" ").pop().replace(/,/g, "");
    var cash_spent = parseFloat($('#cash-spent-entry').val());
    var calculated_ticker = cash_spent/bid_price;
    var calculated_ticker = calculated_ticker.toFixed(2);
    $('#ticket-entry-number').val(calculated_ticker);
    $('#ticket-entry-number').focus();
    $('#cash-spent-entry').focus();
    check_cash_left(cash_spent); 
}

$(document).on("change, keyup", "#ticket-entry-number", updatePrice);
$(document).on("change, keyup", "#cash-spent-entry", updateTicker);



