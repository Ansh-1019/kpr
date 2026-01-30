import { useState } from "react";
import { Box, TextField, Button, Typography, Card, CircularProgress } from "@mui/material";
import ResultCard from "../components/ResultCard";
import axios from "axios";

const CertificateSection = () => {
  const [url, setUrl] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleVerify = async () => {
    if (!url) return;
    setLoading(true);
    setResult(null);
    try {
      const response = await axios.post("/api/bot/verify-certificate", { url });
      setResult(response.data);
    } catch (error) {
      console.error("Verification error:", error);
      setResult({ valid: false, provider: "Error", details: "Failed to connect to server" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ maxWidth: 600, mx: "auto" }}>
      <Card sx={{ p: 4, bgcolor: "#0b0b0f", border: "1px solid rgba(220,38,38,0.3)", borderRadius: 3, mb: 4 }}>
        <Typography variant="h6" color="#e5e7eb" gutterBottom>
          Certificate Verification
        </Typography>
        <Typography variant="body2" color="#9ca3af" sx={{ mb: 3 }}>
          Enter the public certificate URL from Udemy or Coursera.
        </Typography>

        <TextField
          fullWidth
          label="Certificate URL"
          variant="outlined"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          sx={{
            mb: 2,
            "& .MuiOutlinedInput-root": { color: "#fff", "& fieldset": { borderColor: "rgba(220,38,38,0.5)" } },
            "& .MuiInputLabel-root": { color: "#9ca3af" }
          }}
        />

        <Button
          fullWidth
          variant="contained"
          size="large"
          onClick={handleVerify}
          disabled={loading}
          sx={{ background: "linear-gradient(135deg, #dc2626, #7f1d1d)" }}
        >
          {loading ? <CircularProgress size={24} color="inherit" /> : "Verify Certificate"}
        </Button>
      </Card>

      {result && <ResultCard result={result} />}
    </Box>
  );
};

export default CertificateSection;
