/**
 * This is the jQuery way for online.
 *  1) Install onLoad onUnload event callback
 *  2) Call every 30s who is online (whosonline) and then execute the callback
 */

var CheckWhosOnline = function(callback, refreshTime) {
    /** We don't need to have a result. We just send nothing to the url and then... close
     * @param url {String} The url
     */
    function post(url) {
        var post_xhr = new XMLHttpRequest();
        post_xhr.open('POST', url, false);
        post_xhr.send(null);
    }

    var refresh = function() {
            var get_xhr = new XMLHttpRequest();
            get_xhr.open('GET', '/whosonline/', false);
            get_xhr.onreadystatechange = function(evt) {
                if (get_xhr.readyState === 4 && get_xhr.status === 200) {
                    callback(JSON.parse(get_xhr.responseText));
                }
            }
            get_xhr.send(null);
        };
        

    function postOnline() { post('/online/');   }
    function postOffline() { post('/offline/'); }

    if (document.attachEvent) {
        document.attachEvent('onload', postOnline);
        document.attachEvent('onunload', postOffline);
    } else {
        document.addEventListener('load', postOnline, false);
        document.addEventListener('unload', postOffline, false);
    }

    refresh();
    var interval = setInterval(refresh, refreshTime);
};

