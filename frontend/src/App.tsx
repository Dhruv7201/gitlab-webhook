import "./App.css";
import { Routes, Route } from "react-router-dom";
import UserProjectData from "./pages/UserProjectData";
import ChartsPage from "./pages/ChartsPage";
import NotFound from "./pages/NotFound";
import MilestoneTabs from "./components/_tables/MilestoneList";
import IssueDetails from "./pages/IssueDetails";

function App() {
  return (
    <Routes>
      <Route path="/" element={<UserProjectData />} />
      <Route path="/charts" element={<ChartsPage />} />
      <Route path="/milestones" element={<MilestoneTabs />} />
      <Route path="/issue/:issueId" element={<IssueDetails />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}

export default App;
