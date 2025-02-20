import { Behaviour } from "./portfolio.Behaviour.js";
import { ViewModel } from "./portfolio.viewmodel.js";
import { readDocx } from "../../libs/LoadDocx/Loaddocx.js";


export async function Component() {
    try {
        const docFile = await readDocx();
        if (!docFile) {
            throw new Error("No document content received");
        }
        const behaviourInstance = new Behaviour();  
        const viewModelInstance = new ViewModel(docFile);
        return { behaviourInstance, viewModelInstance};

    } catch (error) {
        console.error("Error in Component:", error);
        return null;
    }
}