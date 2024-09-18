import React from "react";
import api from "@/utils/api";
import { useState, useEffect } from "react";
import Notification from "../Notification";
import { useNavigate } from "react-router-dom";

type User = {
  id: string;
  name: string;
  username: string;
};

type Issue = {
  issue_title: string;
  time_spend_on_issue: string;
};

type Project = {
  data: Data[];
};

type Data = {
  project_name: string;
  project_issues: Issue[];
  time_spend_on_project: string;
};

const UserProjectData = () => {
  const navigate = useNavigate();

  const [users, setUsers] = useState<User[]>([]);
  const [workData, setWorkData] = useState<Project | null>(null);

  const handleFetchWork = async (name: string) => {
    api
      .post(`/work`, {
        username: name,
      })
      .then((response) => {
        const data = response.data;
        if (data.status == false) {
          Notification({ message: data.message, type: "error" });
          return;
        }
        setWorkData(data.data);
      })
      .catch((_error) => {
        Notification({ message: "Problem fetching work", type: "error" });
      });
  };

  useEffect(() => {
    navigate("/dashboard");
    api
      .post("/users")
      .then((response) => {
        const data = response.data;
        if (data.status == false) {
          Notification({ message: data.message, type: "error" });
          return;
        }
        setUsers(data.data);
      })
      .catch((_error) => {
        Notification({ message: "Problem fetching users", type: "error" });
      });
  }, []);
  return (
    <div className="container mx-auto p-4">
      <select
        defaultValue=""
        onChange={(e) => handleFetchWork(e.target.value)}
        className="block py-2 px-4 rounded-md shadow-sm border-gray-300 focus:border-indigo-500 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 w-48"
      >
        <option value="" disabled>
          Choose user
        </option>
        {users.map((user, index) => (
          <option key={index} value={user.username} className="text-gray-900">
            {user.name}
          </option>
        ))}
      </select>
      <table className="w-full mt-4 bg-white shadow-md rounded-md overflow-hidden">
        <thead className="bg-gray-100">
          <tr>
            <th className="py-2 px-4 font-medium text-sm text-gray-700">
              Project Name
            </th>
            <th className="py-2 px-4 font-medium text-sm text-gray-700">
              Issue Title
            </th>
            <th className="py-2 px-4 font-medium text-sm text-gray-700">
              Time
            </th>
          </tr>
        </thead>
        <tbody>
          {workData &&
            workData.data.map((project, index) => (
              <React.Fragment key={index}>
                {project.project_issues.map((issue: Issue, index: number) => (
                  <tr
                    key={index}
                    className={index % 2 === 0 ? "bg-gray-50" : "bg-white"}
                  >
                    <td className="py-2 px-4">
                      {index === 0 ? project.project_name : ""}
                    </td>
                    <td className="py-2 px-4">{issue.issue_title}</td>
                    <td className="py-2 px-4">{issue.time_spend_on_issue}</td>
                  </tr>
                ))}
                <tr className="bg-gray-100">
                  <td className="py-2 px-4 font-medium">Total</td>
                  <td className="py-2 px-4"></td>
                  <td className="py-2 px-4 font-medium">
                    {project.time_spend_on_project}
                  </td>
                </tr>
              </React.Fragment>
            ))}
        </tbody>
      </table>
    </div>
  );
};

export default UserProjectData;
