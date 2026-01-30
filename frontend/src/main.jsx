import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";

const theme = createTheme({
  palette: {
    mode: "dark",
    primary: {
      main: "#dc2626", // crimson red
    },
    secondary: {
      main: "#ef4444",
    },
    background: {
      default: "#020202",
      paper: "#0b0b0f",
    },
  },
  typography: {
    fontFamily: "Poppins, Inter, Roboto, Arial, sans-serif",
    h2: { fontWeight: 700 },
    h6: { fontWeight: 500 },
  },
});

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  </React.StrictMode>
);
