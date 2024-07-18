import React from "react";
import { useState, useEffect } from "react";
import Notification from "../../Notification";

type Issue = {
  issue_title: string;
  total_duration: string;
};

type Project = {
  data: Data[];
};

type Data = {
  username: string;
  issues: Issue[];
  time_spend_on_project: string;
};
interface Props {
  selectedProjectId: number;
}
const UserProjectData: React.FC<Props> = ({ selectedProjectId }) => {
  const [workData, setWorkData] = useState<Project | null>(null);
  const api = import.meta.env.VITE_API_URL;

  const renderLabel = (props: any) => {
    const seconds = props;
    var min = null;
    var hr = null;
    var sec = null;

    hr = Math.floor(seconds / 3600);
    if (hr == 0) {
      hr = "00";
    }

    min = Math.floor((seconds % 3600) / 60);
    if (min == 0) {
      min = "00";
    }

    sec = Math.floor(seconds % 60);
    return `${hr}:${min}:${sec}`;
  };

  function formatData(data: any) {
    return {
      ...data,
      data: data.data.map((item: { issues: any[] }) => {
        return {
          ...item,
          issues: item.issues.map((issue) => {
            return {
              ...issue,
              total_duration: renderLabel(issue.total_duration),
            };
          }),
        };
      }),
    };
  }
  useEffect(() => {
    const fetchUsers = async () => {
      if (selectedProjectId === 0) return;
      try {
        const response = await fetch(api + "/user_work_done_list", {
          method: "POST",
          body: JSON.stringify({
            project_id: selectedProjectId,
          }),
          headers: {
            "Content-type": "application/json; charset=UTF-8",
          },
        });
        const data = await response.json();
        if (data.status == false) {
          Notification({ message: data.message, type: "error" });
          return;
        }
        const format_data = formatData(data);
        setWorkData(format_data);
      } catch (error) {
        Notification({ message: "Problem fetching users", type: "error" });
      }
    };
    fetchUsers();
  }, [selectedProjectId]);
  return (
    <div className="container mx-auto p-4">
      <div style={{ height: 50 }}>
        <h1 className="text-2xl font-semibold leading-none tracking-tight">
          Work Done By users
        </h1>
      </div>
      <table className="w-full mt-4 bg-white shadow-md rounded-md overflow-hidden">
        <thead className="bg-gray-100">
          <tr>
            <th className="py-2 px-4 font-medium text-sm text-gray-700">
              Username
            </th>
            <th className="py-2 px-4 font-medium text-sm text-gray-700">
              Issue Title
            </th>
            <th className="py-2 px-4 font-medium text-sm text-gray-700">
              Total Duration
            </th>
          </tr>
        </thead>
        <tbody>
          {workData &&
            workData.data.map((project) => (
              <React.Fragment key={project.username}>
                {project.issues.map((issue: Issue, index: number) => (
                  <tr
                    key={index}
                    className={index % 2 === 0 ? "bg-gray-50" : "bg-white"}
                  >
                    <td className="py-2 px-4">
                      {index === 0 ? project.username : ""}
                    </td>
                    <td className="py-2 px-4">{issue.issue_title}</td>
                    <td className="py-2 px-4">{issue.total_duration}</td>
                  </tr>
                ))}
              </React.Fragment>
            ))}
        </tbody>
      </table>
    </div>
  );
};

export default UserProjectData;
