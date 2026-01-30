import {
  Card,
  Typography,
  Chip,
  Stack,
} from "@mui/material";

const ResultCard = ({ result }) => {
  if (!result) return null;

  // Handle Explicit Errors (e.g. Rate Limits)
  if (result.error) {
    return (
      <Card
        sx={{
          mt: 4,
          p: 3,
          borderRadius: 3,
          background: "linear-gradient(135deg, #7f1d1d, #450a0a)",
          boxShadow: "0 0 25px rgba(0,0,0,0.6)",
          border: "1px solid #ef4444"
        }}
      >
        <Stack spacing={2}>
          <Typography variant="h6" sx={{ color: "#fecaca", display: "flex", alignItems: "center", gap: 1 }}>
            ⚠️ {result.title || "Error"}
          </Typography>
          <Typography sx={{ color: "#f8fafc" }}>
            {result.message}
          </Typography>
        </Stack>
      </Card>
    );
  }

  // Handle Certificate Verification Result
  if (result.hasOwnProperty("valid")) {
    const isVerified = result.valid;
    return (
      <Card
        sx={{
          mt: 4,
          p: 3,
          borderRadius: 3,
          background: isVerified
            ? "linear-gradient(135deg, #052e16, #14532d)"
            : "linear-gradient(135deg, #450a0a, #7f1d1d)",
          boxShadow: "0 0 25px rgba(0,0,0,0.6)",
        }}
      >
        <Stack spacing={2}>
          <Typography variant="h6" sx={{ color: "#f8fafc" }}>
            Certificate Verification
          </Typography>
          <Chip
            label={result.valid ? "Verified Valid" : "Invalid / Not Found"}
            color={result.valid ? "success" : "error"}
            sx={{ width: "fit-content", fontWeight: 600 }}
          />
          <Typography sx={{ color: "#f8fafc" }}>
            <strong>Provider:</strong> {result.provider}
          </Typography>
          <Typography sx={{ color: "#e5e7eb" }}>
            {result.details}
          </Typography>
        </Stack>
      </Card>
    );
  }

  // Handle AI Image Analysis Result
  if (result.hasOwnProperty("is_ai")) {
    const isAi = result.is_ai;
    return (
      <Card
        sx={{
          mt: 4,
          p: 3,
          borderRadius: 3,
          background: isAi
            ? "linear-gradient(135deg, #7c2d12, #9a3412)" // Orange/Red for AI
            : "linear-gradient(135deg, #052e16, #14532d)", // Green for Real
          boxShadow: "0 0 25px rgba(0,0,0,0.6)",
        }}
      >
        <Stack spacing={2}>
          <Typography variant="h6" sx={{ color: "#f8fafc" }}>
            AI Image Analysis
          </Typography>
          <Chip
            label={isAi ? "AI Generated" : "Real Image"}
            color={isAi ? "warning" : "success"}
            sx={{ width: "fit-content", fontWeight: 600 }}
          />
          <Typography sx={{ color: "#f8fafc" }}>
            <strong>Confidence:</strong> {result.confidence}
          </Typography>
          <Typography sx={{ color: "#e5e7eb" }}>
            <strong>Reasoning:</strong> {result.reasoning}
          </Typography>
        </Stack>
      </Card>
    );
  }

  // Legacy Format (fallback)
  if (result.decision) {
    const { mediaType, decision } = result;
    const isVerified = decision.status.toLowerCase().includes("verified");
    return (
      <Card
        sx={{
          mt: 4,
          p: 3,
          borderRadius: 3,
          background: isVerified
            ? "linear-gradient(135deg, #052e16, #14532d)"
            : "linear-gradient(135deg, #450a0a, #7f1d1d)",
          boxShadow: "0 0 25px rgba(0,0,0,0.6)",
        }}
      >
        <Stack spacing={2}>
          <Typography variant="h6" sx={{ color: "#f8fafc" }}>
            Verification Result
          </Typography>
          <Chip
            label={decision.status}
            color={isVerified ? "success" : "error"}
            sx={{ width: "fit-content", fontWeight: 600 }}
          />
          <Typography sx={{ color: "#f8fafc" }}>
            <strong>Media Type:</strong> {mediaType}
          </Typography>
          <Typography sx={{ color: "#f8fafc" }}>
            <strong>Confidence:</strong> {decision.confidence}
          </Typography>
          <ul>
            {decision.reasons.map((r, i) => (
              <li key={i} style={{ color: "#e5e7eb" }}>{r}</li>
            ))}
          </ul>
        </Stack>
      </Card>
    );
  }

  return null;
};

export default ResultCard;
