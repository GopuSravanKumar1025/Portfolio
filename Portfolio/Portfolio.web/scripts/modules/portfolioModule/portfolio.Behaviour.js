export function Behaviour() {
    var Piller = document.body;
    //First Div in Portfolio
    var basements = Object.assign(document.createElement('div'), {className: 'desktop-view', id: 'content'});
    var frameBasement = Object.assign(document.createElement('div'), {className: 'frame desktop-frame', id:'changeScreenSaver'});
    var FirstDiv = document.createElement('div')
    FirstDiv.className = 'Body-div';
    frameBasement.appendChild(FirstDiv)
    basements.appendChild(frameBasement)
    //Top Bar Div
    var SecondSection = Object.assign(document.createElement('div'), {className: 'MobilityAccess', id: 'AccessData'});
    var topBar = document.createElement('div');
    topBar.className = 'TopBar';
    topBar.id = '_TopBar_';
    SecondSection.appendChild(topBar);
    //names for Top Bar
    const Names = [
        "Home",
        "About",
        "Personal Summary",
        "Skills",
        "Experience",
        "Education",
        "Certifications",
        "Additional Projects",
        "GitHub",
        "LinkedIn"
    ]
    //Looping Names in order to automate
    for (var N_ames in Names) {
        if (!Names) {
            console.log('Names Not Found');
        }
        //Span create for names
        var Span_ = document.createElement('span');
        Span_.className = 'names';
        Span_.id = `Onclicknames${N_ames}`

        var para = document.createElement('p');
        para.className = 'text';
        para.id = `text${N_ames}`;
        
        if(N_ames === '10'){
            para.innerHTML = Names[N_ames]
        }else{
            para.innerText = Names[N_ames];
        }

        Span_.appendChild(para)
        topBar.appendChild(Span_)
    }
    var DownloadResume = Object.assign(document.createElement('span'), {className: 'ResumeDownload', id: 'ResumeDownload', innerText: 'Download Resume'});
    topBar.appendChild(DownloadResume);
    //FirstDiv.appendChild(SecondSection)
    //Display Name and image
    var DisplayDiv = document.createElement('div');
    DisplayDiv.className = 'DisplayName_';
    DisplayDiv.id = 'ChangePlaceHolderForMobileView'
    var Displayspan = document.createElement('span');
    Displayspan.className = 'Displayspan';
    var DisplayParaName = document.createElement('p');
    DisplayParaName.className = 'DisplayParaName';
    DisplayParaName.innerText = 'Gopu Sravan Kumar';
    var Display_Proff = document.createElement('p');
    Display_Proff.className = 'DisplayParaName';
    Display_Proff.innerText = 'Junior Software Developer';
    Displayspan.appendChild(DisplayParaName)
    Displayspan.appendChild(Display_Proff)

    //avtar Display
    var AvtSpan = document.createElement('span');
    AvtSpan.className = 'avtspan';
    var avtImg = document.createElement('img');
    avtImg.className = 'avatar';
    avtImg.alt = 'Avatar';
    avtImg.src = '../../../../Portfolio.web/logos/Sravan.jpeg'
    AvtSpan.appendChild(avtImg)
    DisplayDiv.appendChild(Displayspan)
    DisplayDiv.appendChild(AvtSpan)
    SecondSection.appendChild(DisplayDiv)
    FirstDiv.appendChild(SecondSection)


    //Headers
    var Container = document.createElement('div');
    Container.className = 'Contaner';
    var secondContainer = document.createElement('div');
    secondContainer.className = 'secondContainer';
    for (var i = 1; i < Names.length; i++) {
        if (Names[i] === "GitHub") {
            continue;  // Skip GitHub
        }
        if (Names[i] === "LinkedIn") {
            continue;  // Skip LinkedIn
        }
        var ItemDiv = document.createElement('div');
        ItemDiv.className = 'ItemsDiv hidden';
        ItemDiv.id = `ItemsID${i}`;
        ItemDiv.style.setProperty('--animation-delay', `${i * 0.1}s`);
        if (i > 1) { 
            var LineDiv = document.createElement('div');
            LineDiv.className = 'liners';
            secondContainer.appendChild(LineDiv);
        }
        var ContainerHead = document.createElement('span');
        ContainerHead.className = 'ItemsHead';
        ContainerHead.id = `ItemsHead${i}`
        ContainerHead.innerText = Names[i];
        ItemDiv.appendChild(ContainerHead);
        secondContainer.appendChild(ItemDiv)
    }
    
    Container.appendChild(secondContainer)
    FirstDiv.appendChild(Container)
    Piller.appendChild(basements)

    setTimeout(() => {
        const elements = document.querySelectorAll(".hidden");
        const observer = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("show");
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });
        elements.forEach(el => observer.observe(el));
    }, 100);
    var DownloadResume = document.getElementById('ResumeDownload');
    DownloadResume.onclick = function (event) {
        const link = document.createElement('a');
        link.href = '../../../../GopuSravanKumar.docx';
        link.download = 'gopusravankumar.docx';
        link.click();
    }
    var numbers = 10;
    for (var i = 0; i < numbers; i++) {
        var TopbarItem = document.getElementById(`Onclicknames${i}`);
        if (TopbarItem) {
            TopbarItem.onclick = (function (index) {
                return function (event) {
                    if (event.target.innerText === 'Home') {
                        window.location.reload()
                    } else if(event.target.innerText === 'GitHub'){
                        window.open('https://github.com/GopuSravanKumar1025/Portfolio', '_blank');
                    }else if(event.target.innerText === 'LinkedIn'){
                        window.open('https://www.linkedin.com/in/gopu-sravan-kumar-b92593295/', '_blank');
                    }else{
                        var section = document.getElementById(`ItemsID${index}`);
                        if (section) {
                            window.scrollTo({
                                top: section.offsetTop - 205,
                                behavior: "smooth"
                            });
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