// Generated by CoffeeScript 1.4.0
(function() {

  window.addToUrl = function(k, v) {
    var found, key, newSearch, pair, pairs, value, _i, _len, _ref;
    pairs = window.location.search.split('&');
    newSearch = [];
    found = false;
    for (_i = 0, _len = pairs.length; _i < _len; _i++) {
      pair = pairs[_i];
      _ref = pair.split('='), key = _ref[0], value = _ref[1];
      if (k === key) {
        value = v;
        found = true;
      }
      newSearch.push(key + '=' + value);
    }
    if (!found) {
      newSearch.push(k + '=' + v);
    }
    return window.location.search = newSearch.join('&');
  };

}).call(this);
