import { useState } from "react";
import { LoginView } from "./components/LoginView";
import { Shell } from "./components/Shell";
import type { RouteKey } from "./components/nav";
import { Dashboard } from "./components/views/Dashboard";
import { SymmetricView } from "./components/views/SymmetricView";
import { HashView } from "./components/views/HashView";
import { HmacPbkdf2View } from "./components/views/HmacPbkdf2View";
import { EncodingView } from "./components/views/EncodingView";
import { RsaView } from "./components/views/RsaView";
import { EccView } from "./components/views/EccView";
import { KeysView } from "./components/views/KeysView";
import { AuditView } from "./components/views/AuditView";
import { BenchmarkView } from "./components/views/BenchmarkView";
import { DemosView } from "./components/views/DemosView";
import { ScenariosView } from "./components/views/ScenariosView";

export default function App() {
  const [logged, setLogged] = useState(false);
  const [username, setUsername] = useState("");
  const [route, setRoute] = useState<RouteKey>("dashboard");

  if (!logged) {
    return (
      <LoginView
        onLogin={(name) => {
          setUsername(name);
          setLogged(true);
          setRoute("dashboard");
        }}
      />
    );
  }

  return (
    <Shell
      username={username}
      route={route}
      onNavigate={setRoute}
      onLogout={() => {
        setLogged(false);
        setUsername("");
      }}
    >
      {route === "dashboard" && <Dashboard username={username} onNavigate={setRoute} />}
      {route === "symmetric" && <SymmetricView />}
      {route === "hash" && <HashView />}
      {route === "hmac-pbkdf2" && <HmacPbkdf2View />}
      {route === "encoding" && <EncodingView />}
      {route === "rsa" && <RsaView />}
      {route === "ecc" && <EccView />}
      {route === "keys" && <KeysView />}
      {route === "audit" && <AuditView />}
      {route === "benchmark" && <BenchmarkView />}
      {route === "demos" && <DemosView />}
      {route === "scenarios" && <ScenariosView />}
    </Shell>
  );
}
