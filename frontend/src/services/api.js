import axios from "axios";

const API = axios.create({
  baseURL: "/api",
});

export const verifyFile = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await API.post("/verify", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

  return response.data;
};

export const analyzeImage = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await API.post("/bot/analyze-image", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

  return response.data;
};
