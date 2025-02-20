import { module } from "./Portfolio.web/scripts/modules/modules.js";
function changeTitle() {
  Object.defineProperty(navigator, 'userAgent', {
    get: function () { return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"; }
  });
  if (navigator.userAgent.match(/Android/i)) {
    window.location.href = "https://gopusravan.com";
  }
  if (/iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream) {
    document.querySelector("meta[name=viewport]").setAttribute("content", "width=1024");
}

  var LoadModule = module()
  var url = window.location.pathname;
  var segments = url.split('/');
  var pageTitle = segments[segments.length - 1];
  if (pageTitle === '') {
    pageTitle = 'Home';
  }
  document.title = pageTitle.charAt(0).toUpperCase() + pageTitle.slice(1);


}
window.onload = changeTitle();

