// check if console.log is available
if(window['console'] === undefined) window.console = { log: function(){} };

// allow jQuery to chain .log
if('jQuery' in window) jQuery.fn.log = function(msg) { console.log("%s: %o", msg, this); return this; };

// set namespace
var SHOP = {};

jQuery(document).ready(function ($) {
    SHOP.cart = {
        empty: function(delete_url, callback){
            callback = (callback) ? callback : function(){};
            $.post(delete_url, {}, callback);
        },
        addItem: function(item_add_url, item_id, callback){
            callback = (callback) ? callback : function(){};
            $.post(item_add_url, {'add_item_id': item_id}, callback);
        },
        updateItemQuantity: function(update_item_url, quantity, callback){
            callback = (callback) ? callback : function(){};
            $.post(update_item_url, {'item_quantity': quantity}, callback);	  
        },
        deleteItem: function(delete_item_url, callback){
            callback = (callback) ? callback : function(){};
            $.post(delete_item_url, {}, callback);
        },
    }
});
