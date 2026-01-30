import { Typography } from "@mui/material";

const AudioSection = () => {
  return (
    <>
      <Typography variant="h6" gutterBottom>
        Audio Verification (Future Scope)
      </Typography>

      <Typography>
        This module will detect AI-generated voices, deepfake audio, and voice
        cloning using spectral and temporal analysis.
      </Typography>

      <Typography sx={{ mt: 2 }} color="text.secondary">
        🚧 Coming Soon
      </Typography>
    </>
  );
};

export default AudioSection;
