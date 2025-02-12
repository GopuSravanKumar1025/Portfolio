import { Behaviour } from "./portfolio.Behaviour.js";
import { ViewModel } from "./portfolio.viewmodel.js";
import { Navigation } from "./Navigation.js";
import { readDocx } from "../../libs/LoadDocx/Loaddocx.js";

export async function Component() {
    try {
        const docFile = await readDocx();
        if (!docFile) {
            throw new Error("No document content received");
        }
        const behaviourInstance = new Behaviour();  
        const viewModelInstance = new ViewModel(docFile);
        const NavigationInstance = new Navigation();
        return { behaviourInstance, viewModelInstance, NavigationInstance };

    } catch (error) {
        console.error("Error in Component:", error);
        return null;
    }
}