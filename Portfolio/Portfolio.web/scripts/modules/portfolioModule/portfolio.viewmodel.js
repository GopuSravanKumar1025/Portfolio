export function ViewModel(docFile) {
    function extractSections(text) {
        const sections = [];
        const professionalSummary = text.match(/Professional Summary\n([\s\S]+?)\n\nPersonal Summary/);
        if (professionalSummary) sections.push({ type: "Professional Summary", content: professionalSummary[1].trim() });
        const personalSummary = text.match(/Personal Summary\n([\s\S]+?)\n\nSkills/);
        if (personalSummary) sections.push({ type: "Personal Summary", content: personalSummary[1].trim() });
        const skills = text.match(/Skills\n([\s\S]+?)\n\nExperience/);
        if (skills) sections.push({ type: "Skills", content: skills[1].trim() });
        const experience = text.match(/Experience\n([\s\S]+?)\n\nEducation/);
        if (experience) sections.push({ type: "Experience", content: experience[1].trim() });
        const education = text.match(/Education and Training\n([\s\S]+?)\n\nCertifications/);
        if (education) sections.push({ type: "Education and Training", content: education[1].trim() });
        const certifications = text.match(/Certifications\n([\s\S]+?)\n\nAdditional Projects/);
        if (certifications) sections.push({ type: "Certifications", content: certifications[1].trim() });
        const projects = text.match(/Additional Projects\n([\s\S]+?)(?=\n[A-Z][a-zA-Z ]*\n|$)/);
        if (projects) sections.push({ type: "Additional Projects", content: projects[1].trim() });
        return sections;
    }
    const sections = extractSections(docFile);
    for (var i = 0; i < sections.length; i++) {
        var Id = `ItemsID${i + 1}`;
        var ItemsID = document.getElementById(Id);
        if (sections[i].type === "Skills") {
            const SkillsSet = sections[i].content;
            const SeparatedList = SkillsSet.split("\n")
                .map(line => line.split(" – "))
                .map(arr => ({
                    skill: arr[0].replace(/\d+/g, "").trim(),
                    experience: parseInt(arr[1]) || 0
                }));
            var skillsContainer = document.createElement("div");
            skillsContainer.className = "SkillsContainer";
            const createSkillItem = (item) => {
                var skillItem = Object.assign(document.createElement("div"), { className: "SkillItem" });
                var skillName = Object.assign(document.createElement("span"), { className: "SkillName", innerText: item.skill });
                var progressBar = Object.assign(document.createElement("div"), { className: "ProgressBar" });
                var progressFill = Object.assign(document.createElement("div"), { className: "ProgressFill" });
                var percentageLabel = Object.assign(document.createElement("span"), { className: "PercentageLabel" });
                let experiencePercentage = 70;
                if (item.experience === 4) {
                    experiencePercentage = 98;
                } else if (item.experience === 3) {
                    experiencePercentage = 94;
                } else if (item.experience === 2) {
                    experiencePercentage = 88;
                } else if (item.experience === 1) {
                    experiencePercentage = 80;
                } else if (item.experience >= 5) {
                    experiencePercentage = 98;
                }
                percentageLabel.innerText = `${experiencePercentage}%`;
                progressFill.style.width = `0%`;
                progressBar.append(progressFill);
                skillItem.append(skillName, progressBar, percentageLabel);
                skillsContainer.append(skillItem);
                const observer = new IntersectionObserver(entries => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            progressFill.style.transition = "width 2s ease-in-out";
                            progressFill.style.width = `${experiencePercentage}%`;
                        }
                    });
                }, { threshold: 0.5 });
                observer.observe(skillItem);
            };
            SeparatedList.forEach(item => {
                if (item.skill !== "") {
                    createSkillItem(item);
                }
            });
            ItemsID.appendChild(skillsContainer);
        } else if (sections[i].type === "Experience") {
            var ITRoleName = sections[i].content.split("\t");
            var StartDataEndData = ITRoleName[1].split('\n\n');
            var ITCompanyName = sections[i].content.split("\n\n");
            var RoleDescrption = ITRoleName[2].split(/\n\s*\n/).filter(line => line.trim() !== "Software Developer");
            var ExperienceConatiner = Object.assign(document.createElement('div'), { className: 'BodySpan' });
            var ITExperienceDiv = Object.assign(document.createElement('div'), { className: 'ITExperienceDiv' });
            var ITRoleNameDiv = Object.assign(document.createElement('div'), { className: 'ITRoleNameDiv' });
            var NameSpaceDiv = Object.assign(document.createElement('div'), { className: 'NameSpaceDiv' });
            var Rolespan = Object.assign(document.createElement('span'), { className: 'Rolename', innerText: ITRoleName[0] });
            var Datespan = Object.assign(document.createElement('span'), { className: 'Rolename', innerText: StartDataEndData[0] });
            var CompanySpan = Object.assign(document.createElement('span'), { className: 'Rolename', innerText: ITCompanyName[1] });
            var CompanynamespaceDiv = Object.assign(document.createElement('div'), { className: 'CompanynamespaceDiv' });
            CompanynamespaceDiv.appendChild(CompanySpan);
            var DescriptionDiv = Object.assign(document.createElement('div'), { className: 'DescriptionDiv' });
            RoleDescrption.slice(1).forEach(text => {
                var Descspan = document.createElement('span');
                Descspan.className = 'Descspan';
                var li = Object.assign(document.createElement('li'), { className: 'Description', innerText: text });
                Descspan.appendChild(li);
                DescriptionDiv.appendChild(Descspan);
            });
            [Rolespan, Datespan].forEach(el => NameSpaceDiv.appendChild(el));
            [NameSpaceDiv, CompanynamespaceDiv].forEach(el => ITRoleNameDiv.appendChild(el));
            [ITRoleNameDiv, DescriptionDiv].forEach(el => ITExperienceDiv.appendChild(el));
            ExperienceConatiner.appendChild(ITExperienceDiv);
            var SoftwareDeveloperDiv = Object.assign(document.createElement('div'), { className: 'SoftwareContainer' });
            var SoftwareRoleName = Object.assign(document.createElement('div'), { className: 'SWName' });
            var SoftwareNameSpaceDiv = Object.assign(document.createElement('div'), { className: 'NameSpaceDiv' });
            var SoftwareSpan = Object.assign(document.createElement('span'), { className: 'SwDEVname', id: 'SoftwareDevName', innerText: 'Software Developer  12/2020 to 08/2022' });
            var AddressSpan = Object.assign(document.createElement('span'), { className: 'AddressName', id: 'SoftwareDevName', innerText: 'Cura Grc Private Limited, Hyderabad, India' });
            var CompanyIndex = ITCompanyName.indexOf("Cura GRC Private Limited \t Hyderabad, India ");
            var DevRoleDescription = CompanyIndex !== -1 ? ITCompanyName.slice(CompanyIndex + 1) : [];
            [SoftwareSpan, AddressSpan].forEach(appargs => SoftwareNameSpaceDiv.appendChild(appargs));
            SoftwareRoleName.appendChild(SoftwareNameSpaceDiv)
            SoftwareDeveloperDiv.appendChild(SoftwareRoleName)
            ExperienceConatiner.appendChild(SoftwareDeveloperDiv)
            var SWDEVDescription = Object.assign(document.createElement('div'), { className: 'Descdev' });
            DevRoleDescription.slice(0).forEach(data => {
                var DevDescspan = document.createElement('span');
                DevDescspan.className = 'DevDescspan';
                var li = Object.assign(document.createElement('li'), { className: 'SWDescription', innerText: data });
                DevDescspan.appendChild(li);
                SWDEVDescription.appendChild(DevDescspan);
            });
            SoftwareRoleName.appendChild(SWDEVDescription)
            ItemsID.appendChild(ExperienceConatiner);
        } else if (sections[i].type === "Education and Training") {
            var Education = sections[i].content.split('\n\n');
            var EducationContainer = Object.assign(document.createElement('div'), { className: 'BodySpan' });
            var MastersContainer = Object.assign(document.createElement('div'), { className: 'MastersContainer' });
            var DegreeConatiner = Object.assign(document.createElement('div'), { className: 'DegreeConatiner' });
            var MastersName = Object.assign(document.createElement('div'), { className: 'MastersName' });
            var mastersSpan = Object.assign(document.createElement('span'), { className: 'DegreeName', id: 'MastersDegree', innerText: Education[0] });
            var MastersAddress = Object.assign(document.createElement('span'), { className: 'MastersAddress', id: 'MastersDegree', innerText: Education[1] });
            var dissertationContainer = Object.assign(document.createElement('div'), { className: 'Dissertation' });
            var DissertationName = Object.assign(document.createElement('span'), { className: 'DissertationName', innerText: 'Waste management on geospatial enhancement Optmisation:' });
            var DissertationDesc = Object.assign(document.createElement('span'), { className: 'DissertationDesc', innerText: ` ${Education[3]}` });
            var DegreeNameDiv = Object.assign(document.createElement('div'), { className: 'DegreeNameDiv' });
            var DegreeNameSpan = Object.assign(document.createElement('span'), { className: 'UnderGraduate', id: 'MastersDegree', innerText: Education[5] });
            var DegreeAddress = Object.assign(document.createElement('span'), { className: 'UnderGraduate', id: 'MastersDegree', innerText: Education[6] })
            var DegreeDesc = Object.assign(document.createElement('div'), { className: 'DegreeDescDiv' });
            var splitEdu = Education[8].split(':');
            var DegreeSpan = Object.assign(document.createElement('span'), { className: 'DegreeSpec', innerText: `${splitEdu[0]}:` });
            var DegreedescSpan = Object.assign(document.createElement('span'), { className: 'DegreeDescSpan', innerText: splitEdu[1] })
            DegreeDesc.append(DegreeSpan, DegreedescSpan)
            DegreeNameDiv.append(DegreeNameSpan, DegreeAddress);
            DegreeConatiner.append(DegreeNameDiv, DegreeDesc)
            dissertationContainer.append(DissertationName, DissertationDesc)
            MastersName.append(mastersSpan, MastersAddress);
            MastersContainer.append(MastersName, dissertationContainer)
            EducationContainer.append(MastersContainer, DegreeConatiner)
            ItemsID.appendChild(EducationContainer);
        } else if (sections[i].type === "Additional Projects") {
            var AdditionalContainerBody = Object.assign(document.createElement("div"), { className: 'BodySpan' });
            var AdditionalProjects = sections[i].content.split('\n\n');
            for (var l in AdditionalProjects) {
                if (AdditionalProjects[l].includes(':')) {
                    var DivToAdd = Object.assign(document.createElement('div'), { className: 'AdditionalDivSpec' });
                    var split_ = AdditionalProjects[l].split(':');
                    var AdditionalSpan = Object.assign(document.createElement('span'), { className: 'AdditionalName', innerText: `${split_[0]}` });
                    var AdditionalDescSpan = Object.assign(document.createElement('span'), { className: 'AdditionalDesc', innerText: split_[1] });
                    DivToAdd.appendChild(AdditionalDescSpan);
                    AdditionalContainerBody.append(AdditionalSpan, DivToAdd);
                }
            }
            ItemsID.appendChild(AdditionalContainerBody);
        } else {
            var ContainerBody = document.createElement("span");
            ContainerBody.className = "BodySpan";
            ContainerBody.id = "SpanBody";
            ContainerBody.innerText = sections[i].content;
            ItemsID.appendChild(ContainerBody);
        }
    }    
}