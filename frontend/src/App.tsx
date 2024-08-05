import "./App.css";
import { Routes, Route } from "react-router-dom";
import UserProjectData from "./pages/UserProjectData";
import ChartsPage from "./pages/ChartsPage";
import NotFound from "./pages/NotFound";
import IssueDetails from "./pages/IssueDetails";
import FilterPage from "./pages/Filterpage";
import Milestones from "./pages/Milestones";
function App() {
  return (
    <Routes>
      <Route path="/" element={<UserProjectData />} />
      <Route path="/charts" element={<ChartsPage />} />
      <Route path="/issue/:issueId" element={<IssueDetails />} />
      <Route path="/filters" element={<FilterPage />} />
      <Route path="/milestones" element={<Milestones />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}

export default App;
