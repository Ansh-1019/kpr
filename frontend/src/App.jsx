import { useState } from "react";
import {
  Box,
  Container,
  Tabs,
  Tab,
  Typography,
  Card,
} from "@mui/material";

import CertificateSection from "./sections/CertificateSection";
import ImageSection from "./sections/ImageSection";
import VideoSection from "./sections/VideoSection";
import AudioSection from "./sections/AudioSection";

function App() {
  const [tab, setTab] = useState(0);

  return (
    <Box
      sx={{
        minHeight: "100vh",
        background:
          "radial-gradient(circle at top, #1a0505 0%, #020202 65%)",
        display: "flex",
        alignItems: "center",
        py: 8,
      }}
    >
      <Container maxWidth="md">
        {/* HERO */}
        <Box textAlign="center" mb={6}>
          <Typography
            variant="h2"
            sx={{
              color: "#fca5a5",
              textShadow: "0 0 20px rgba(220,38,38,0.4)",
            }}
          >
            NAME
          </Typography>

          <Typography
            variant="h6"
            sx={{ color: "#9ca3af", maxWidth: 720, mx: "auto", mt: 1 }}
          >
            AI-powered verification platform for certificates, images,
            and deepfake video detection
          </Typography>
        </Box>

        {/* GLASS CARD */}
        <Card
          sx={{
            backdropFilter: "blur(18px)",
            background:
              "linear-gradient(135deg, rgba(20,0,0,0.85), rgba(5,5,5,0.85))",
            borderRadius: 4,
            boxShadow:
              "0 30px 60px rgba(220,38,38,0.25)",
            p: 4,
            border: "1px solid rgba(220,38,38,0.25)",
          }}
        >
          <Tabs
            value={tab}
            onChange={(e, newValue) => setTab(newValue)}
            centered
            textColor="primary"
            indicatorColor="primary"
            sx={{
              mb: 4,
              "& .MuiTab-root": {
                color: "#e5e7eb",
                fontWeight: 600,
              },
            }}
          >
            <Tab label="Certificate" />
            <Tab label="Image" />
            <Tab label="Video" />
            <Tab label="Audio (Future)" />
          </Tabs>

          {tab === 0 && <CertificateSection />}
          {tab === 1 && <ImageSection />}
          {tab === 2 && <VideoSection />}
          {tab === 3 && <AudioSection />}
        </Card>

        {/* FOOTER */}
        <Box textAlign="center" mt={6}>
          <Typography variant="caption" sx={{ color: "#6b7280" }}>
            © 2026 NAME • Privacy-first • Zero file storage
          </Typography>
        </Box>
      </Container>
    </Box>
  );
}

export default App;
