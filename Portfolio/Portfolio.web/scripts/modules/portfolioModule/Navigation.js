export function Navigation() {
    var numbers = 8;
    for (var i = 0; i < numbers; i++) {
        var TopbarItem = document.getElementById(`Onclicknames${i}`);
        if (TopbarItem) {
            TopbarItem.onclick = (function (index) {
                return function (event) {
                    if(event.target.innerText === 'Home'){
                        window.location.reload()
                    }else{
                        var section = document.getElementById(`ItemsID${index}`);
                        if (section) {
                            section.scrollIntoView({ behavior: "smooth" });
                        } else {
                            console.warn(`Section with ID "ItemsID${index}" not found.`);
                        }
                    }
                };
            })(i);
        } else {
            console.warn(`Topbar item with ID "Onclicknames${i}" not found.`);
        }
    }
}
