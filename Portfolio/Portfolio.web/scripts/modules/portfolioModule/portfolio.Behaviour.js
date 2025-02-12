export function Behaviour() {
    var Piller = document.body;
    //First Div in Portfolio
    var FirstDiv = document.createElement('div')
    FirstDiv.className = 'Body-div';
    //Top Bar Div
    var topBar = document.createElement('div');
    topBar.className = 'TopBar';
    topBar.id = '_TopBar_';
    //names for Top Bar
    const Names = [
        "Home",
        "About",
        "Personal Summary",
        "Skills",
        "Experience",
        "Education",
        "Certifications",
        "Additional Projects"
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
        para.innerText = Names[N_ames];

        Span_.appendChild(para)
        topBar.appendChild(Span_)
    }
    var DownloadResume = Object.assign(document.createElement('span'), {className: 'ResumeDownload', id: 'ResumeDownload', innerText: 'Download Resume'});
    topBar.appendChild(DownloadResume)
    FirstDiv.appendChild(topBar)
    //Display Name and image
    var DisplayDiv = document.createElement('div');
    DisplayDiv.className = 'DisplayName_';
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
    avtImg.src = 'http://localhost/Portfolio.web/logos/Sravan.jpeg'
    AvtSpan.appendChild(avtImg)
    DisplayDiv.appendChild(Displayspan)
    DisplayDiv.appendChild(AvtSpan)
    FirstDiv.appendChild(DisplayDiv)


    //Headers
    var Container = document.createElement('div');
    Container.className = 'Contaner';
    var secondContainer = document.createElement('div');
    secondContainer.className = 'secondContainer';
    for (var i = 1; i < Names.length; i++) {
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
    Piller.appendChild(FirstDiv)

    setTimeout(() => {
        const elements = document.querySelectorAll(".hidden");
        const observer = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("show");
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.2 });
        elements.forEach(el => observer.observe(el));
    }, 100); 
    
}