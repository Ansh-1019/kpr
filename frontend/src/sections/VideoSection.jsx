import { useState } from "react";
import FileUploader from "../components/FileUploader";
import ResultCard from "../components/ResultCard";

const VideoSection = () => {
  const [result, setResult] = useState(null);

  return (
    <>
      <FileUploader
        accept=".mp4,.mov"
        description="Upload a video to verify authenticity using frame and metadata analysis."
        onResult={setResult}
      />
      <ResultCard result={result} />
    </>
  );
};

export default VideoSection;
