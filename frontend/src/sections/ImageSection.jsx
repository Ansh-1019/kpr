import { useState } from "react";
import FileUploader from "../components/FileUploader";
import ResultCard from "../components/ResultCard";
import { analyzeImage } from "../services/api";

const ImageSection = () => {
  const [result, setResult] = useState(null);

  return (
    <>
      <FileUploader
        accept=".png,.jpg,.jpeg"
        description="Upload an image to verify whether it is authentic or manipulated."
        onResult={setResult}
        uploadFunction={analyzeImage}
      />
      <ResultCard result={result} />
    </>
  );
};

export default ImageSection;
