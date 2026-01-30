import { useState } from "react";
import {
  Button,
  Typography,
  Card,
  Stack,
} from "@mui/material";
import UploadFileIcon from "@mui/icons-material/CloudUpload";
import { verifyFile } from "../services/api";

const FileUploader = ({ accept, description, onResult, uploadFunction = verifyFile }) => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleVerify = async () => {
    if (!file) {
      alert("Please select a file");
      return;
    }

    setLoading(true);
    try {
      const result = await uploadFunction(file);
      onResult(result);
    } catch {
      alert("Verification failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card
      sx={{
        background: "#0b0b0f",
        borderRadius: 3,
        p: 3,
        border: "1px solid rgba(220,38,38,0.3)",
      }}
    >
      <Stack spacing={2}>
        <Typography sx={{ color: "#e5e7eb" }}>
          {description}
        </Typography>

        <Button
          variant="outlined"
          component="label"
          startIcon={<UploadFileIcon />}
          sx={{
            borderColor: "#dc2626",
            color: "#fca5a5",
          }}
        >
          Select File
          <input
            hidden
            type="file"
            accept={accept}
            onChange={(e) => setFile(e.target.files[0])}
          />
        </Button>

        {file && (
          <Typography variant="body2" sx={{ color: "#9ca3af" }}>
            📄 {file.name}
          </Typography>
        )}

        <Button
          variant="contained"
          size="large"
          onClick={handleVerify}
          disabled={loading}
          sx={{
            background:
              "linear-gradient(135deg, #dc2626, #7f1d1d)",
            boxShadow:
              "0 0 20px rgba(220,38,38,0.4)",
          }}
        >
          {loading ? "Analyzing..." : "Verify Authenticity"}
        </Button>

        <Typography variant="caption" sx={{ color: "#6b7280" }}>
          🔒 Files are analyzed securely and never stored
        </Typography>
      </Stack>
    </Card>
  );
};

export default FileUploader;
