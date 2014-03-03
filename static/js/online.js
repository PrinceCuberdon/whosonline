/**
 * This is the jQuery way for online.
 *  1) Install onLoad onUnload event callback
 *  2) Call every 30s who is online (whosonline) and then execute the callback
 * @TODO: Remove jQuery dependencies to jQuery
 */
jCheckWhosOnline = function(callback, refreshTime) {
    var interval = 0,
        refresh = function() {
            $.getJSON('/whosonline/', callback);
        };
        
    refresh();
    $(window)
        .on('load', function() {$.post('/online/')})
        .on('unload', function() {$.post('/offline/')});
        
    interval = setInterval(refresh, refreshTime);
};

