mobileCheck = function() {
    var isMobile = (/iphone|ipod|ipad|android|ie|blackberry|fennec/).test
         (navigator.userAgent.toLowerCase());
    return isMobile;
}
if (mobileCheck()){
var btnScrollDown = document.querySelector('#scroll_down');
btnScrollDown.remove();
}
(function() {
  'use strict';

  var btnScrollDown = document.querySelector('#scroll_down');
  if (btnScrollDown == null){
    return
  }
  function scrollDown() {
    var windowCoords = document.documentElement.clientHeight;
    (function scroll() {
      if (window.pageYOffset < windowCoords) {
        window.scrollBy(0, 200);
        setTimeout(scroll, 0);
      }
      if (window.pageYOffset > windowCoords) {
        window.scrollTo(0, windowCoords);
      }
    })();
  }

  btnScrollDown.addEventListener('click', scrollDown);
})();
