import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { validateToken } from "@/utils/api";
import api from "@/utils/api";

// Define RepoList type with proper nesting for subgroups
type RepoList = {
  id: string;
  name: string;
  subgroup: boolean;
  subgroups?: RepoList[]; // Optional subgroups for nested repos/projects
};

const RepoSettings = () => {
  const [repoList, setRepoList] = useState<RepoList[]>([]);
  const [expandedRepos, setExpandedRepos] = useState<{ [key: string]: boolean }>({});
  const [loading, setLoading] = useState<boolean>(true);
  const navigate = useNavigate();

  // Validate token on component mount
  useEffect(() => {
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

  // Fetch the top-level repo settings on component mount
  useEffect(() => {
    const fetchRepoSettings = async () => {
      try {
        setLoading(true);
        const response = await api.post("/repo-settings", {});
        const data = response.data.data;
        setRepoList(Object.entries(data).map(([id, repo]) => ({ id, ...repo })));
        setLoading(false);
      } catch (error) {
        console.error(error);
        setLoading(false);
      }
    };

    fetchRepoSettings();
  }, []);

  // Function to handle subgroup expansion
  const handleExpand = async (repoId: string) => {
    if (expandedRepos[repoId]) {
      // If it's already expanded, collapse the subgroup
      setExpandedRepos((prev) => ({ ...prev, [repoId]: false }));
    } else {
      // If it's not expanded, fetch subgroups/projects
      try {
        const response = await api.post("/repo-settings", { subgroup: repoId });
        const data = response.data.data;
        const subgroupsOrProjects = Object.entries(data).map(([id, repo]) => ({ id, ...repo }));

        // Update the repoList with the fetched subgroups for the expanded repo
        setRepoList((prevRepoList) =>
          updateRepoWithSubgroups(prevRepoList, repoId, subgroupsOrProjects)
        );

        // Expand the repo
        setExpandedRepos((prev) => ({ ...prev, [repoId]: true }));
      } catch (error) {
        console.error("Error loading subgroups/projects:", error);
      }
    }
  };

  // Recursive function to update the repoList state with fetched subgroups
  const updateRepoWithSubgroups = (repoList: RepoList[], repoId: string, subgroups: RepoList[]): RepoList[] => {
    return repoList.map((repo) => {
      if (repo.id === repoId) {
        return { ...repo, subgroups }; // Update the repo with its fetched subgroups
      }
      // If this repo has nested subgroups, update those recursively
      if (repo.subgroups) {
        return { ...repo, subgroups: updateRepoWithSubgroups(repo.subgroups, repoId, subgroups) };
      }
      return repo;
    });
  };

  // Recursive function to render subgroups or projects
  const renderSubgroups = (subgroups: RepoList[], level = 0) => {
    return (
      <div className={`pl-${level * 6} mt-2`}>
        {subgroups.map((subgroup) => (
          <div
            key={subgroup.id}
            className={`flex items-center justify-between bg-gray-50 rounded-lg p-2 mb-2 shadow-sm ${subgroup.subgroups ? "border-l-2 border-gray-300" : ""}`}
          >
            <div className={`flex items-center ${subgroup.subgroups ? "cursor-pointer" : ""}`} onClick={() => subgroup.subgroups && handleExpand(subgroup.id)}>
              <span className={`font-medium ${subgroup.subgroups ? "text-gray-900" : "text-gray-700"}`}>{subgroup.name}</span>
              {subgroup.subgroup && (
                <button
                  className="ml-4 text-gray-600 hover:text-gray-800 focus:outline-none"
                  onClick={() => handleExpand(subgroup.id)}
                >
                  {expandedRepos[subgroup.id] ? (
                    <span className="text-lg">▼</span>
                  ) : (
                    <span className="text-lg">▶</span>
                  )}
                </button>
              )}
            </div>

            {/* If there are nested subgroups and the repo is expanded, recursively render them */}
            {expandedRepos[subgroup.id] && subgroup.subgroups && (
              <div>{renderSubgroups(subgroup.subgroups, level + 1)}</div>
            )}
          </div>
        ))}
      </div>
    );
  };

  if (loading) {
    return <div className="text-center text-lg py-4">Loading...</div>;
  }

  return (
    <div className="p-6 bg-gray-100 min-h-screen">
      <h2 className="text-2xl font-bold mb-6">Repository Settings</h2>
      {repoList.length === 0 ? (
        <div className="text-gray-500">No repositories found.</div>
      ) : (
        repoList.map((repo) => (
          <div
            key={repo.id}
            className="mb-4 p-4 bg-white rounded-lg shadow-md border border-gray-200"
          >
            <div className="flex justify-between items-center">
              <h1 className="text-lg font-semibold">{repo.name}</h1>
              {repo.subgroup && (
                <button
                  className="text-gray-700 hover:text-gray-900 focus:outline-none"
                  onClick={() => handleExpand(repo.id)}
                >
                  {expandedRepos[repo.id] ? (
                    <span className="text-lg">▼</span>
                  ) : (
                    <span className="text-lg">▶</span>
                  )}
                </button>
              )}
            </div>

            {/* If subgroups/projects are present and the repo is expanded, display them */}
            {expandedRepos[repo.id] && repo.subgroups && (
              <div className="mt-2">{renderSubgroups(repo.subgroups)}</div>
            )}
          </div>
        ))
      )}
    </div>
  );
};

export default RepoSettings;
