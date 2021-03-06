// Special Javascript functions called for filling out modals with information or validating inputs
// to avoid sending invalid information to the database


// Currency 'Formatter' taken from "How to format a number as a currency value in JavaScript"
// https://flaviocopes.com/how-to-format-number-as-currency-javascript/

const formatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  minimumFractionDigits: 2
});

const buyButton = document.getElementById('modal-buy-button');
const sellButton = document.getElementById('modal-sell-button');

// function builds up the buy-coin-modal with respective data depending on which coin the user selects
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

// function builds up the sell-coin-modal with respective data depending on which coin the user selects
$(document).on("click", ".open-sell-coin-modal-link", function () {
    var selectedCoinSymbol = $(this).attr('data-id');
    var selectedCoinCard = $(this).closest('.card-list-coin');
    var selectedCoinTitle = selectedCoinCard.find('.card-coin-name-symbol').html();
    var selectedCoinName = selectedCoinCard.find('.card-coin-name').html();
    var selectedCoinIcon = selectedCoinCard.find('.card-coin-icon').html();
    var selectedCoinLatestPrice = selectedCoinCard.find('.card-coin-latest-price').html();
    var selectedCoinAskPrice = selectedCoinCard.find('.card-coin-ask-price').html();
    var availableTicker = selectedCoinCard.find('.card-coin-available-ticker').html();
    $("#modal-sell-coin-header").html(selectedCoinTitle);
    $("#modal-sell-coin-icon").html(selectedCoinIcon);
    $("#modal-sell-coin-latest-price").html(selectedCoinLatestPrice);
    $("#modal-sell-coin-ask-price").html(selectedCoinAskPrice);
    $("#modal-available-ticker").html(availableTicker);
    $('#modal-coin-symbol').html(selectedCoinSymbol.replace(/USDT/g,""));
    $('#submit-sell-coin-symbol').val(selectedCoinSymbol);
    $('#submit-sell-coin-name').val(selectedCoinName);
    $('#submit-sell-coin-latest-price').val(selectedCoinLatestPrice);
    $('#submit-sell-coin-ask-price').val(selectedCoinAskPrice);
});

// Function checks if funds are enough for buying coins and rejects invalid ticker inputs
function check_cash_left_and_valid_ticker_entry(cash_spent,ticker){
    var submitBuyButton =  $('#modal-buy-button');
    var available_cash = $('#modal-cash-available').html().split(" ").pop().replace(/,/g, "");
    cash_left = available_cash - cash_spent;
    if (cash_left >= 0.0 && ticker >= 0.01) {
        // cash left >= 0 and ticker >= 0.01: both conditions are correct. 
        buyButton.disabled = false;
        submitBuyButton.tooltip('remove');
        submitBuyButton.removeClass('tooltipped');
        submitBuyButton.removeAttr('data-position');
        submitBuyButton.removeAttr('data-tooltip');
        submitBuyButton.removeAttr('data-tooltip-id');
    } else if (cash_left < 0.00 || ticker < 0.01) {
        buyButton.disabled = true;
        submitBuyButton.addClass('tooltipped');
        submitBuyButton.attr('data-position', 'top');
        if (cash_left < 0.00) {
            // Not enough funds in wallet
            submitBuyButton.attr('data-tooltip', 'You do not have enough cash available to make this transaction. Please add more funds first to your wallet.');
        } else if (ticker < 0.01 ) {
            // Selected ticker is too low for a transaction
            submitBuyButton.attr('data-tooltip', 'You need to select at least 0.01 ticker in order to make a purchase.');
        } else {
            // Both conditions are wrong
            submitBuyButton.attr('data-tooltip', 'You need to select at least 0.01 ticker and add more funds to your wallet to keep buying coins.');
        }
        // Initialize tooltip
        submitBuyButton.tooltip({delay: 50});
    }
    
}

// Function checks if coins are enough for selling and rejects invalid cash inputs
function check_ticker_left_and_valid_cash_entry(cash_entry,ticker){
    var submitSellButton =  $('#modal-sell-button');
    var available_ticker = $('#modal-available-ticker').html().replace(/,/g, "");
    var ticker_left = available_ticker-ticker;
    if (ticker_left >= 0.00 && cash_entry >= 0.01 && ticker >= 0.01) {
        sellButton.disabled=false;
        submitSellButton.removeClass('tooltipped');
        submitSellButton.removeAttr('data-position');
        submitSellButton.removeAttr('data-tooltip');
        submitSellButton.removeAttr('data-tooltip-id');
    } else if (ticker_left < 0.00 || cash_entry < 0.01 || ticker < 0.01) {
        sellButton.disabled=true;
        submitSellButton.addClass('tooltipped');
        submitSellButton.attr('data-position', 'top');
        if (ticker_left < 0.00) {
            // Not enough coins available in wallet for sale
            submitSellButton.attr('data-tooltip', 'You do not have enough coins available to sell.');
        } else if (cash_entry < 0.01) {
            // Selected cash is too low for a transaction
            submitSellButton.attr('data-tooltip', 'You need to select a valid cash value to exchange for this sale.');
        } else if (ticker < 0.01) {
            submitSellButton.attr('data-tooltip', 'You need to sell at least 0.01 coins to make a sale.');
        } 
        else {
            // Both conditions are wrong
            submitSellButton.attr('data-tooltip', 'Please enter valid numbers to proceed with a purchase');
        }
        // Initialize tooltip
        submitSellButton.tooltip();
    }
}

// Function called when user enters a specific ticker in input field
function updateSpentCash(){
    var bid_price = $('#modal-buy-coin-bid-price').html().split(" ").pop().replace(/,/g, "");
    var ticker = parseFloat($('#ticket-entry-number').val());
    var cash_spent = bid_price*ticker;
    cash_spent = cash_spent.toFixed(2);
    $('#cash-spent-entry').val(cash_spent);
    $('#cash-spent-entry').focus();
    $('#ticket-entry-number').focus();
    check_cash_left_and_valid_ticker_entry(cash_spent,ticker);
}

// Function called when user enters a specific cash spent amount in input field
function updateTickerBuy(){
    var bid_price = $('#modal-buy-coin-bid-price').html().split(" ").pop().replace(/,/g, "");
    var cash_spent = parseFloat($('#cash-spent-entry').val());
    var calculated_ticker = cash_spent/bid_price;
    calculated_ticker = calculated_ticker.toFixed(2);
    $('#ticket-entry-number').val(calculated_ticker);
    $('#ticket-entry-number').focus();
    $('#cash-spent-entry').focus();
    check_cash_left_and_valid_ticker_entry(cash_spent,calculated_ticker); 
}

// Function called when user enters a specific ticker in input field
function updateExchangeCash(){
    var ask_price = $('#modal-sell-coin-ask-price').html().split(" ").pop().replace(/,/g, "");
    var ticker = parseFloat($('#sell-ticket-entry-number').val());
    var cash_exchange = ask_price*ticker;
    cash_exchange = cash_exchange.toFixed(2);
    $('#cash-exchange-entry').val(cash_exchange);
    $('#cash-exchange-entry').focus();
    $('#sell-ticket-entry-number').focus();
    check_ticker_left_and_valid_cash_entry(cash_exchange,ticker);
}

// Function called when user enters a specific cash spent amount in input field
function updateTickerSell(){
    var ask_price = $('#modal-sell-coin-ask-price').html().split(" ").pop().replace(/,/g, "");
    var cash_exchange = parseFloat($('#cash-exchange-entry').val());
    var calculated_ticker = cash_exchange/ask_price;
    calculated_ticker = calculated_ticker.toFixed(2);
    $('#sell-ticket-entry-number').val(calculated_ticker);
    $('#sell-ticket-entry-number').focus();
    $('#cash-exchange-entry').focus();
    check_ticker_left_and_valid_cash_entry(cash_exchange,calculated_ticker); 
}

$(document).on("change, keyup", "#ticket-entry-number", updateSpentCash);
$(document).on("change, keyup", "#cash-spent-entry", updateTickerBuy);
$(document).on("change, keyup", "#sell-ticket-entry-number", updateExchangeCash);
$(document).on("change, keyup", "#cash-exchange-entry", updateTickerSell);

// Function called when user wants to add extra funds to available cash, modal displays correct information

function addFundsModal(btn){
    var selectedAmount = $(btn).attr('data-id');
    $('#add-funds-modal').modal('close');
    $('#confirm-add-funds-modal').modal('open');
    $('.add-funds-amount').html("US$ " + selectedAmount);
    var available_cash = $('#cash-available-invisible').html().replace(/,/g, "");
    var new_total_cash = parseFloat(available_cash) + parseFloat(selectedAmount.replace(/,/g, ""));
    $('#new-cash-available').html(formatter.format(new_total_cash));
    $('#confirm-add-funds-input').val(selectedAmount);
}

