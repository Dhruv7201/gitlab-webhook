import React from "react";
import { Link } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import api, { validateToken } from "@/utils/api";
import Notification from "@/Notification";

type Issue = {
  id: number;
  title: string;
  OnHold: number;
  on_hold_since: string;
  subgroup_name: string;
  project_name: string;
  project_url: string;
  issue_url: string;
};

const Loader = () => (
  <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 align-baseline">
    <div className="text-white text-lg flex items-center animate-pulse">
      <span>Loading</span>
      <div className="dot-container">
        <div className="dot"></div>
        <div className="dot"></div>
        <div className="dot"></div>
      </div>
    </div>
  </div>
);

const OnHold = () => {
  const [issues, setIssues] = React.useState<Issue[]>([]);
  const [searchQuery, setSearchQuery] = React.useState<string>("");
  const [loading, setLoading] = React.useState<boolean>(false);
  const navigate = useNavigate();
  React.useEffect(() => {
    if (localStorage.getItem("token")) {
      validateToken(localStorage.getItem("token") as string).then((res) => {
        if (!res) {
          localStorage.removeItem("token");

          navigate("/login");
        }
      });
    } else {
      navigate("/login");
    }
  }, [navigate]);
  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value.toLowerCase());
  };
  const filteredIssues = issues.filter(
    (issues) =>
      issues.title.toLowerCase().includes(searchQuery) ||
      issues.OnHold.toString().includes(searchQuery)
  );

  React.useEffect(() => {
    api
      .post("/get_onhold", {})
      .then((res) => {
        if (res.data.status === false) {
          Notification({ message: res.data.message, type: "error" });
          return;
        }
        console.log(res.data.data);
        setIssues(res.data.data);
      })
      .catch((err) => {
        console.log(err);
        Notification({ message: "Problem fetching data", type: "error" });
      });
  }, []);

  const openSubgroup = (issue: Issue) => {
    setLoading(true);
    api
      .post("/get_subgroup_link", { subgroup_name: issue.subgroup_name })
      .then((res) => {
        setLoading(false);
        if (res.data.status === false) {
          Notification({ message: res.data.message, type: "error" });
          return;
        }
        window.open(res.data.data, "_blank");
      })
      .catch((err) => {
        setLoading(false);
        Notification({ message: "Problem fetching data", type: "error" });
      });
  };
  return (
    <>
      {loading && <Loader />}
      <div className="p-4">
        <input
          type="text"
          placeholder="Search Issue by Issue title or project name"
          className="p-2 w-full border rounded-md"
          onChange={handleSearch}
        />
      </div>
      <div className="p-4">
        <h1 className="text-2xl font-semibold">Issues</h1>
        {filteredIssues.length > 0 ? (
          filteredIssues.map((issue) => (
            <div
              key={issue.id}
              className="flex justify-between items-center p-4 border-b border-gray-200 hover:bg-gray-100"
            >
              <div className="flex items-center">
                <div className="ml-4 text-start">
                  <p className="text-lg font-semibold underline">
                    <Link to={`/issue/${issue.id}`}>{issue.title}</Link>
                  </p>
                  <p className="text-sm text-gray-500 hover:underline cursor-pointer">
                    <a
                      href={issue.project_url}
                      target="_blank"
                      rel="noreferrer"
                    >
                      {issue.project_name}
                    </a>
                  </p>
                </div>
              </div>
              <div className="flex items-start">
                <p
                  className="text-sm text-gray-500 hover:underline cursor-pointer"
                  onClick={() => openSubgroup(issue)}
                >
                  Subgroup: {issue.subgroup_name}
                </p>
                <p className="text-sm text-gray-500 ml-4 hover:underline cursor-pointer">
                  <a href={issue.issue_url} target="_blank" rel="noreferrer">
                    Issue Url
                  </a>
                </p>
                <p className="text-sm text-gray-500 ml-4 hover:underline cursor-pointer">
                  <a href={issue.project_url} target="_blank" rel="noreferrer">
                    Project Url
                  </a>
                </p>
              </div>
            </div>
          ))
        ) : (
          <p className="text-center text-gray-500">No issues found</p>
        )}
      </div>
    </>
  );
};

export default OnHold;
