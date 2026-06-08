import { createRoot } from "react-dom/client";
import { AuthProvider } from "@/stores/auth";
import { AppRouter } from "@/router";
import "./styles/index.css";

createRoot(document.getElementById("root")!).render(
  <AuthProvider>
    <AppRouter />
  </AuthProvider>
);
