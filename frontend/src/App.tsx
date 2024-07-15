import "./App.css";
import { Routes, Route } from "react-router-dom";
import UserProjectData from "./pages/UserProjectData";
import ChartsPage from "./pages/ChartsPage";
import NotFound from "./pages/NotFound";

function App() {
  return (
    <Routes>
      <Route path="/" element={<UserProjectData />} />
      <Route path="/charts" element={<ChartsPage />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}

export default App;
