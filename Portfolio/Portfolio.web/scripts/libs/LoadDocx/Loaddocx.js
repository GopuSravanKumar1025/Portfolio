export async function readDocx() {
        try {
            const response = await fetch("../../../../GopuSravanKumar.docx");
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
