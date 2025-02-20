import { Component } from "./portfolioModule/portfolio.component.js";


export function module(){
    try {
        var ModuleComponent = Component();
        return {ModuleComponent};
    } catch (error) {
        console.error("Error in Component:", error);
        return null;
    }
    
}