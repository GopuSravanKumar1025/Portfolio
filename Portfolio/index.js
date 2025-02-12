import { module } from "./Portfolio.web/scripts/modules/modules.js";
function changeTitle() {
  if (window.location.href === "http://localhost/portfolio") {
    var LoadModule = module()
    var url = window.location.pathname;
    var segments = url.split('/');
    var pageTitle = segments[segments.length - 1];
    if (pageTitle === '') {
      pageTitle = 'Home';
    }
    document.title = pageTitle.charAt(0).toUpperCase() + pageTitle.slice(1);
  } else if (window.location.href === "http://localhost:3000/") {
    var LoadModule = module()
    var url = window.location.pathname;
    var segments = url.split('/');
    var pageTitle = segments[segments.length - 1];
    if (pageTitle === '') {
      pageTitle = 'Portfolio';
    }
    const faviconPath = 'http://localhost:3000/Portfolio.web/logos/Sravan.jpeg';
    const link = document.createElement('link');
    link.rel = 'icon';
    link.href = faviconPath;
    document.head.appendChild(link);
    document.title = pageTitle.charAt(0).toUpperCase() + pageTitle.slice(1);
  }

}
window.onload = changeTitle();

