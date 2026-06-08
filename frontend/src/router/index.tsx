import { BrowserRouter, Routes, Route, Navigate, Outlet } from "react-router-dom";
import { useAuth } from "@/stores/auth";
import { Shell } from "@/components/Shell";
import { LoginView } from "@/components/LoginView";
import { Dashboard } from "@/views/Dashboard";
import { SymmetricView } from "@/views/SymmetricView";
import { HashView } from "@/views/HashView";
import { HmacPbkdf2View } from "@/views/HmacPbkdf2View";
import { EncodingView } from "@/views/EncodingView";
import { RsaView } from "@/views/RsaView";
import { EccView } from "@/views/EccView";
import { KeysView } from "@/views/KeysView";
import { AuditView } from "@/views/AuditView";
import { BenchmarkView } from "@/views/BenchmarkView";
import { DemosView } from "@/views/DemosView";
import { ScenariosView } from "@/views/ScenariosView";

function RequireAuth() {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return (
    <Shell>
      <Outlet />
    </Shell>
  );
}

function PublicOnly() {
  const { isAuthenticated } = useAuth();
  if (isAuthenticated) return <Navigate to="/dashboard" replace />;
  return <Outlet />;
}

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<PublicOnly />}>
          <Route path="/login" element={<LoginView />} />
        </Route>
        <Route element={<RequireAuth />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/symmetric" element={<SymmetricView />} />
          <Route path="/hash" element={<HashView />} />
          <Route path="/hmac-pbkdf2" element={<HmacPbkdf2View />} />
          <Route path="/encoding" element={<EncodingView />} />
          <Route path="/rsa" element={<RsaView />} />
          <Route path="/ecc" element={<EccView />} />
          <Route path="/keys" element={<KeysView />} />
          <Route path="/audit" element={<AuditView />} />
          <Route path="/benchmark" element={<BenchmarkView />} />
          <Route path="/demos" element={<DemosView />} />
          <Route path="/scenarios" element={<ScenariosView />} />
        </Route>
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
