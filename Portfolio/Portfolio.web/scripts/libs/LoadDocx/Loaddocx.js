export async function readDocx() {
    if(window.location.href === "http://localhost/portfolio"){
        try {
            const response = await fetch("http://localhost/gopusravankumar.docx");
            if (!response.ok) {
                throw new Error("File not found or failed to load.");
            }
            const arrayBuffer = await response.arrayBuffer();
            const result = await mammoth.extractRawText({ arrayBuffer: arrayBuffer });
            return result.value;
        } catch (error) {
            console.error("Error fetching or reading DOCX file:", error);
            return null;
        }
    }else if(window.location.href === "http://localhost:3000/"){
        try {
            const response = await fetch("http://localhost:3000/gopusravankumar.docx");
            if (!response.ok) {
                throw new Error("File not found or failed to load.");
            }
            const arrayBuffer = await response.arrayBuffer();
            const result = await mammoth.extractRawText({ arrayBuffer: arrayBuffer });
            return result.value;
        } catch (error) {
            console.error("Error fetching or reading DOCX file:", error);
            return null;
        }
    }
    
}
