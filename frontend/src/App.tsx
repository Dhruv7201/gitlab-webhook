import "./App.css";
import { Routes, Route } from "react-router-dom";
import UserProjectData from "./pages/UserProjectData";
import ChartsPage from "./pages/ChartsPage";
import NotFound from "./pages/NotFound";
import IssueDetails from "./pages/IssueDetails";
import FilterPage from "./pages/Filterpage";
import Layout from "./layout/Layout";
import UsersPage from "./pages/UsersPage";
import Users from "./pages/Users";
import Issues from "./pages/Issues";
import Login from "./pages/Login";
import LabelSettings from "./pages/LabelSettings";
import Settings from "./pages/Settings";
import UserSettings from "./pages/UserSettings";
import RepoSettings from "./pages/RepoSettings";
import OnHold from "./pages/OnHold";

function App() {
  return (
    <Routes>
      <Route path="/" element={<UserProjectData />} />
      <Route path="/login" element={<Login />} />
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
        path="/user/:userId"
        element={
          <Layout>
            <UsersPage />
          </Layout>
        }
      />

      <Route
        path="/users"
        element={
          <Layout>
            <Users />
          </Layout>
        }
      />
      <Route
        path="/issues"
        element={
          <Layout>
            <Issues />
          </Layout>
        }
      />
      <Route
        path="/onHold"
        element={
          <Layout>
            <OnHold />
          </Layout>
        }
      />
      <Route
        path="/settings"
        element={
          <Layout>
            <Settings />
          </Layout>
        }
      />
      <Route
        path="/settings/label-settings"
        element={
          <Layout>
            <LabelSettings />
          </Layout>
        }
      />
      <Route
        path="/settings/user-settings"
        element={
          <Layout>
            <UserSettings />
          </Layout>
        }
      />
      <Route
        path="/settings/repo-settings"
        element={
          <Layout>
            <RepoSettings />
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
