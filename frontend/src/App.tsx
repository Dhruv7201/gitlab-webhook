import "./App.css";
import { Routes, Route } from "react-router-dom";
import UserProjectData from "./pages/UserProjectData";
import ChartsPage from "./pages/ChartsPage";
import NotFound from "./pages/NotFound";
import IssueDetails from "./pages/IssueDetails";
import FilterPage from "./pages/Filterpage";
import Milestones from "./pages/Milestones";
import Layout from "./layout/Layout";
function App() {
  return (
    <Routes>
      <Route path="/" element={<UserProjectData />} />
      <Route
        path="/dashboard"
        element={
          <Layout>
            <ChartsPage />
          </Layout>
        }
      />
      <Route
        path="/charts"
        element={
          <Layout>
            <ChartsPage />
          </Layout>
        }
      />
      <Route
        path="/issue/:issueId"
        element={
          <Layout>
            <IssueDetails />
          </Layout>
        }
      />
      <Route
        path="/filters"
        element={
          <Layout>
            <FilterPage />
          </Layout>
        }
      />
      <Route
        path="/milestones"
        element={
          <Layout>
            <Milestones />
          </Layout>
        }
      />
      <Route
        path="*"
        element={
          <Layout>
            <NotFound />
          </Layout>
        }
      />
    </Routes>
  );
}

export default App;
